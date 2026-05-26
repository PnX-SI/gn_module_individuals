import pytest
from datetime import datetime
from sqlalchemy import func, select

from geonature.tests.fixtures import *
from geonature.tests.fixtures import _app, _session, app, users
from geonature.utils.config import config as gn_config
from geonature.utils.env import db
from geonature.core.gn_commons.models import TModules
from geonature.core.gn_permissions.models import PermAction, PermObject, Permission
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
def device_with_deployment(device, individual):
    dep = IndividualDeployments(
        id_tracking_device=device.id_tracking_device,
        id_individual=individual.id_individual,
        id_capture=1,
        install_date=datetime(2024, 1, 1),
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

    target_permissions = {
        "admin_user": {"actions": "CRUDV", "scope": None},
        "self_user": {"actions": "R", "scope": 1},
    }

    with db.session.begin_nested():
        for username, config in target_permissions.items():
            user = users.get(username)
            if user is None:
                continue
            for action_code in config["actions"]:
                action = actions.get(action_code)
                if action is None or object_all is None:
                    continue
                exists = db.session.scalar(
                    select(Permission).where(
                        Permission.id_role == user.id_role,
                        Permission.id_module == module.id_module,
                        Permission.id_action == action.id_action,
                        Permission.id_object == object_all.id_object,
                    )
                )
                if exists is None:
                    permission = Permission(
                        id_role=user.id_role,
                        id_module=module.id_module,
                        id_action=action.id_action,
                        id_object=object_all.id_object,
                        scope_value=config["scope"],
                    )
                    db.session.add(permission)

    return module
