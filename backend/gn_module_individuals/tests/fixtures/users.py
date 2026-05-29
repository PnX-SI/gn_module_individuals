import pytest
from sqlalchemy import select

from geonature.core.gn_permissions.models import PermAction, PermObject, Permission
from geonature.utils.env import db
from pypnusershub.db.models import Application, Profils as Profil, User, UserApplicationRight

from gn_module_individuals import MODULE_CODE

def _scope_value(scope):
    return None if scope == 3 else scope

@pytest.fixture
def individuals_user_factory(users, ensure_individuals_module):
    def create_user(username, *, actions="R", scope=1):
        app = db.session.scalar(select(Application).where(Application.code_application == "GN"))
        profil = db.session.scalar(select(Profil).where(Profil.nom_profil == "Lecteur"))
        object_all = db.session.scalar(select(PermObject).filter_by(code_object="ALL"))
        with db.session.begin_nested():
                user = User(
                    groupe=False,
                    active=True,
                    identifiant=username,
                    password=username,
                    nom_role=username,
                    prenom_role="Test",
                    id_organisme=users["admin_user"].id_organisme,
                )
                db.session.add(user)
                db.session.flush()

                db.session.add(
                    UserApplicationRight(
                        id_role=user.id_role,
                        id_application=app.id_application,
                        id_profil=profil.id_profil,
                    )
                )

                for code_action in actions:
                    action = db.session.scalar(select(PermAction).filter_by(code_action=code_action))
                    db.session.add(
                        Permission(
                            id_role=user.id_role,
                            id_module=ensure_individuals_module.id_module,
                            id_action=action.id_action,
                            id_object=object_all.id_object,
                            scope_value=_scope_value(scope),
                        )
                    )

        return user

    return create_user

@pytest.fixture
def individuals_users(individuals_user_factory):
    return {
        "admin_user": individuals_user_factory("admin_user", actions="CRUD", scope=3),
        "self_user": individuals_user_factory("self_user", actions="CRUD", scope=1),
        "noright_user": individuals_user_factory("noright_user", actions="", scope=0),
    }