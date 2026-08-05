import datetime as dt
import pytest
from sqlalchemy import func, select

from geonature.tests.fixtures import *
from geonature.tests.fixtures import _app, _session, app, users
from geonature.utils.config import config as gn_config
from geonature.utils.env import db
from geonature.core.gn_commons.models import TModules
from geonature.core.gn_permissions.models import PermAction, PermObject, Permission
from geonature.tests.utils import get_id_nomenclature
from pypnusershub.tests.fixtures import teardown_logout_user

from gn_module_individuals import MODULE_CODE, MODULE_LABEL, MODULE_PICTO
from gn_module_individuals.blueprint import blueprint as indiv_blueprint
from gn_module_individuals.models import TrackingDevices, IndividualDeployments
from gn_module_individuals.tests.fixtures import *

pytest.endpoint = ""


@pytest.fixture
def client(app):
    if "individuals.list_devices" not in app.view_functions:
        module_config = gn_config.get(MODULE_CODE, {})
        url_prefix = module_config.get("MODULE_API", "/individuals")
        if not url_prefix.startswith("/"):
            url_prefix = f"/{url_prefix}"
        app.register_blueprint(indiv_blueprint, url_prefix=url_prefix)
    return app.test_client()


@pytest.fixture
def device_with_deployment(device, individual, capture):
    dep = IndividualDeployments(
        id_tracking_device=device.id_tracking_device,
        id_individual=individual.id_individual,
        id_capture=capture.id_capture,
        id_nomenclature_deployment_type=get_id_nomenclature(
            nomenclature_type_mnemonique="TYPE_MARQUAGE", cd_nomenclature="4"
        ),
        id_nomenclature_deployment_location=get_id_nomenclature(
            nomenclature_type_mnemonique="LOC_MARQUAGE", cd_nomenclature="3"
        ),
        install_date=dt.datetime(2024, 1, 1),
    )
    with db.session.begin_nested():
        db.session.add(dep)
        db.session.flush()
    return device


@pytest.fixture(scope="session", autouse=True)
def ensure_individuals_module(app, users):
    """Ensure the module record and baseline permissions exist for tests."""
    module = db.session.scalar(select(TModules).filter_by(module_code=MODULE_CODE))
    if module is None:
        with db.session.begin_nested():
            module = TModules(
                module_code=MODULE_CODE,
                module_label=MODULE_LABEL,
                module_path=MODULE_CODE.lower(),
                module_picto=MODULE_PICTO,
                active_frontend=True,
                active_backend=True,
                ng_module=MODULE_CODE.lower(),
            )
            db.session.add(module)
        module = db.session.scalar(select(TModules).filter_by(module_code=MODULE_CODE))

    actions = {
        code: db.session.scalar(select(PermAction).filter_by(code_action=code)) for code in "CRUDV"
    }
    object_all = db.session.scalar(select(PermObject).filter_by(code_object="ALL"))

    # Créer les objets métier du module s'ils n'existent pas encore
    with db.session.begin_nested():
        for code, description in [
            ("DEVICES", "Gestion des individus"),
            ("SAMPLES", "Gestion des échantillons dans Individus"),
        ]:
            if db.session.scalar(select(PermObject).filter_by(code_object=code)) is None:
                db.session.add(PermObject(code_object=code, description_object=description))

    object_individuals = db.session.scalar(select(PermObject).filter_by(code_object="INDIVIDUALS"))

    # Permissions sur ALL (lecture globale du module)
    all_permissions = {
        "admin_user": {"actions": "RV", "scope": None},
        "self_user": {"actions": "R", "scope": 1},
    }
    # Permissions sur INDIVIDUALS (C/U/D discriminés)
    individuals_permissions = {
        "admin_user": {"actions": "CUD", "scope": None},
        "self_user": {"actions": "UD", "scope": 1},
    }

    def _add_permissions(target_map, perm_object):
        with db.session.begin_nested():
            for username, config in target_map.items():
                user = users.get(username)
                if user is None or perm_object is None:
                    continue
                for action_code in config["actions"]:
                    action = actions.get(action_code)
                    if action is None:
                        continue
                    exists = db.session.scalar(
                        select(Permission).where(
                            Permission.id_role == user.id_role,
                            Permission.id_module == module.id_module,
                            Permission.id_action == action.id_action,
                            Permission.id_object == perm_object.id_object,
                        )
                    )
                    if exists is None:
                        db.session.add(
                            Permission(
                                id_role=user.id_role,
                                id_module=module.id_module,
                                id_action=action.id_action,
                                id_object=perm_object.id_object,
                                scope_value=config["scope"],
                            )
                        )

    _add_permissions(all_permissions, object_all)
    _add_permissions(individuals_permissions, object_individuals)

    return module


def add_user_permission(
    module_code, user, scope, type_code_object, code_action="CRUVED", sensitivity_filter=None
):
    """
    Add permissions to a user in a module.

    Parameters
    ----------
    module_code : str
        Code of the module to add the permission to.
    user : User
        User to add the permission to.
    scope : int
        Scope value for the permission.
    type_code_object : str
        Type of the object to add the permission to.
    code_action : str, optional
        Code of the action to add the permission for. Default is "CRUVED".

    Notes
    -----
    The function will add the permission to the specified module and object with the given scope.
    If the scope is 3, the scope_value will be set to None.
    """
    module = db.session.execute(
        select(TModules).where(TModules.module_code == module_code)
    ).scalar_one()
    actions = {
        code: db.session.execute(
            select(PermAction).where(PermAction.code_action == code)
        ).scalar_one()
        for code in code_action
    }
    with db.session.begin_nested():
        if scope > 0:
            object_all = db.session.scalars(
                select(PermObject).where(PermObject.code_object == type_code_object)
            ).all()
            for action in actions.values():
                for obj in object_all + module.objects:
                    permission = Permission(
                        role=user,
                        action=action,
                        module=module,
                        object=obj,
                        scope_value=scope if scope != 3 else None,
                        sensitivity_filter=sensitivity_filter,
                    )
                    db.session.add(permission)


@pytest.fixture(scope="session")
def create_user():
    def _create_user(
        username,
        organisme=None,
        scope=None,
        sensitivity_filter=False,
        modules=None,
    ):
        app = db.session.execute(
            select(Application).where(Application.code_application == "GN")
        ).scalar_one()
        profil = db.session.execute(
            select(Profil).where(Profil.nom_profil == "Lecteur")
        ).scalar_one()

        if not modules:
            modules = db.session.scalars(select(TModules)).all()

        type_code_object = [
            "MONITORINGS_MODULES",
            "MONITORINGS_GRP_SITES",
            "MONITORINGS_SITES",
            "MONITORINGS_VISITES",
            "ALL",
        ]

        # do not commit directly on current transaction, as we want to rollback all changes at the end of tests
        with db.session.begin_nested():
            user = User(
                groupe=False,
                active=True,
                organisme=organisme,
                identifiant=username,
                password=username,
                nom_role=username,
                prenom_role=username,
            )
            db.session.add(user)
        # user must have been commited for user.id_role to be defined
        with db.session.begin_nested():
            # login right
            right = UserApplicationRight(
                id_role=user.id_role, id_application=app.id_application, id_profil=profil.id_profil
            )
            db.session.add(right)

        for module in modules:
            for code_object in type_code_object:
                add_user_permission(
                    module.module_code,
                    user,
                    scope,
                    code_object,
                    code_action="CRUVED",
                    sensitivity_filter=sensitivity_filter,
                )

        return user

    return _create_user
