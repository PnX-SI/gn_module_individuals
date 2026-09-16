import pytest
from flask import url_for

from pypnusershub.tests.utils import set_logged_user

from geonature.utils.env import db

from gn_module_individuals.tests.conftest import add_user_permission
from gn_module_individuals.utils.errors import ApiErrorCode


@pytest.fixture
def target_module(modules, users):
    """A module distinct from INDIVIDUALS, with U+D granted only to admin_user."""
    module = modules[0]
    add_user_permission(module.module_code, users["admin_user"], 3, "ALL", code_action="UD")
    return module


@pytest.fixture
def individual_linked_to_module(individual, target_module):
    with db.session.begin_nested():
        individual.modules.append(target_module)
        db.session.flush()
    return individual


# ===========================================================================
# GET /individuals/<id_individual>/modules  (list_individual_modules)
# ===========================================================================


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestListIndividualModules:

    def test_unauthenticated_returns_401(self, individual):
        r = self.client.get(
            url_for("individuals.list_individual_modules", id_individual=individual.id_individual)
        )
        assert r.status_code == 401

    def test_forbidden_without_rights(self, users, individual):
        set_logged_user(self.client, users["noright_user"])
        r = self.client.get(
            url_for("individuals.list_individual_modules", id_individual=individual.id_individual)
        )
        assert r.status_code == 403

    def test_unknown_individual_returns_404(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_individual_modules", id_individual=-1))
        assert r.status_code == 404

    def test_returns_empty_list_when_no_module_linked(self, users, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(
            url_for("individuals.list_individual_modules", id_individual=individual.id_individual)
        )
        assert r.status_code == 200
        assert r.get_json() == []

    def test_returns_linked_modules_with_can_unlink_flag(
        self, users, target_module, individual_linked_to_module
    ):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(
            url_for(
                "individuals.list_individual_modules",
                id_individual=individual_linked_to_module.id_individual,
            )
        )
        payload = r.get_json()
        assert len(payload) == 1
        assert payload[0]["id_module"] == target_module.id_module
        assert payload[0]["can_unlink"] is True

    def test_self_user_without_target_module_rights_sees_can_unlink_false(
        self, users, target_module, individual_linked_to_module
    ):
        """self_user has U+D on INDIVIDUALS but not on target_module. Granted a
        broader read scope here since individual_linked_to_module is digitised
        by admin_user, outside self_user's default "own" (scope=1) read scope."""
        add_user_permission("INDIVIDUALS", users["self_user"], 3, "INDIVIDUALS", code_action="R")
        set_logged_user(self.client, users["self_user"])
        r = self.client.get(
            url_for(
                "individuals.list_individual_modules",
                id_individual=individual_linked_to_module.id_individual,
            )
        )
        assert r.status_code == 200
        assert r.get_json()[0]["can_unlink"] is False


# ===========================================================================
# POST /individuals/<id_individual>/modules  (link_individual_module)
# ===========================================================================


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestLinkIndividualModule:

    def test_unauthenticated_returns_401(self, individual, target_module):
        r = self.client.post(
            url_for("individuals.link_individual_module", id_individual=individual.id_individual),
            json={"id_module": target_module.id_module},
        )
        assert r.status_code == 401

    def test_unknown_individual_returns_404(self, users, target_module):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.link_individual_module", id_individual=-1),
            json={"id_module": target_module.id_module},
        )
        assert r.status_code == 404

    def test_missing_id_module_returns_400(self, users, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.link_individual_module", id_individual=individual.id_individual),
            json={},
        )
        assert r.status_code == 400
        assert r.get_json()["name"] == ApiErrorCode.VALIDATION_ERROR.value

    def test_non_integer_id_module_returns_400(self, users, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.link_individual_module", id_individual=individual.id_individual),
            json={"id_module": "not-an-integer"},
        )
        assert r.status_code == 400

    def test_unknown_module_returns_404(self, users, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.link_individual_module", id_individual=individual.id_individual),
            json={"id_module": -1},
        )
        assert r.status_code == 404

    def test_user_without_target_module_rights_returns_403(self, users, individual, target_module):
        """self_user has U+D on INDIVIDUALS but not on target_module."""
        set_logged_user(self.client, users["self_user"])
        r = self.client.post(
            url_for("individuals.link_individual_module", id_individual=individual.id_individual),
            json={"id_module": target_module.id_module},
        )
        assert r.status_code == 403
        assert r.get_json()["name"] == ApiErrorCode.INSUFFICIENT_PERMISSIONS.value

    def test_user_without_any_rights_returns_403(self, users, individual, target_module):
        set_logged_user(self.client, users["noright_user"])
        r = self.client.post(
            url_for("individuals.link_individual_module", id_individual=individual.id_individual),
            json={"id_module": target_module.id_module},
        )
        assert r.status_code == 403

    def test_authorized_user_links_module(self, users, individual, target_module):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.link_individual_module", id_individual=individual.id_individual),
            json={"id_module": target_module.id_module},
        )
        assert r.status_code == 201
        assert r.get_json()["id_module"] == target_module.id_module
        assert target_module in individual.modules

    def test_already_linked_returns_409(self, users, target_module, individual_linked_to_module):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for(
                "individuals.link_individual_module",
                id_individual=individual_linked_to_module.id_individual,
            ),
            json={"id_module": target_module.id_module},
        )
        assert r.status_code == 409
        assert r.get_json()["name"] == ApiErrorCode.ALREADY_LINKED.value


# ===========================================================================
# DELETE /individuals/<id_individual>/modules/<id_module>  (unlink_individual_module)
# ===========================================================================


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestUnlinkIndividualModule:

    def test_unauthenticated_returns_401(self, target_module, individual_linked_to_module):
        r = self.client.delete(
            url_for(
                "individuals.unlink_individual_module",
                id_individual=individual_linked_to_module.id_individual,
                id_module=target_module.id_module,
            )
        )
        assert r.status_code == 401

    def test_unknown_individual_returns_404(self, users, target_module):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.delete(
            url_for(
                "individuals.unlink_individual_module",
                id_individual=-1,
                id_module=target_module.id_module,
            )
        )
        assert r.status_code == 404

    def test_not_linked_returns_404(self, users, individual, target_module):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.delete(
            url_for(
                "individuals.unlink_individual_module",
                id_individual=individual.id_individual,
                id_module=target_module.id_module,
            )
        )
        assert r.status_code == 404

    def test_user_without_target_module_rights_returns_403(
        self, users, target_module, individual_linked_to_module
    ):
        set_logged_user(self.client, users["self_user"])
        r = self.client.delete(
            url_for(
                "individuals.unlink_individual_module",
                id_individual=individual_linked_to_module.id_individual,
                id_module=target_module.id_module,
            )
        )
        assert r.status_code == 403

    def test_authorized_user_unlinks_module(
        self, users, target_module, individual_linked_to_module
    ):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.delete(
            url_for(
                "individuals.unlink_individual_module",
                id_individual=individual_linked_to_module.id_individual,
                id_module=target_module.id_module,
            )
        )
        assert r.status_code == 204
        assert target_module not in individual_linked_to_module.modules
