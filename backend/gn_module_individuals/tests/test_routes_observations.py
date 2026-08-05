import pytest
from flask import url_for

from pypnusershub.tests.utils import set_logged_user

from gn_module_individuals.utils.errors import ApiErrorCode

EXPECTED_FIELDS = {
    "id_capture",
    "id_individual",
    "additional_data",
    "individual",
}

# ===========================================================================
# GET /observations  (list_observations)
# ===========================================================================


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestListObservations:
    def test_unauthenticated_returns_401(self):
        r = self.client.get(url_for("individuals.list_observations"))
        assert r.status_code == 401

    def test_forbidden_without_rights(self, users):
        set_logged_user(self.client, users["noright_user"])
        r = self.client.get(url_for("individuals.list_observations"))
        assert r.status_code == 403

    def test_returns_200_with_list(self, users, observation):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_observations"))
        assert r.status_code == 200
        assert isinstance(r.get_json(), list)

    def test_item_contains_expected_fields(self, users, observation):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_observations"))
        item = next(
            i
            for i in r.get_json()
            if i["id_capture"] == observation.id_capture
            and i["id_individual"] == observation.id_individual
        )
        missing = EXPECTED_FIELDS - item.keys()
        assert not missing, f"Missing fields in item: {missing}"
        assert item["individual"]["id_individual"] == observation.id_individual

    def test_filter_by_id_capture(self, users, observations):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(
            url_for("individuals.list_observations", id_capture=observations[0].id_capture)
        )
        assert r.status_code == 200
        items = r.get_json()
        assert len(items) == 1
        assert items[0]["id_capture"] == observations[0].id_capture

    def test_filter_by_id_individual(self, users, observations):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(
            url_for("individuals.list_observations", id_individual=observations[0].id_individual)
        )
        assert r.status_code == 200
        items = r.get_json()
        assert len(items) == 1
        assert items[0]["id_individual"] == observations[0].id_individual

    def test_scope_restricts_to_own_data(self, users, observations):
        """observations[0]'s capture is digitised by admin_user, observations[1]'s by self_user."""
        set_logged_user(self.client, users["self_user"])
        r = self.client.get(url_for("individuals.list_observations"))
        assert r.status_code == 200
        captures_seen = {item["id_capture"] for item in r.get_json()}
        assert observations[1].id_capture in captures_seen
        assert observations[0].id_capture not in captures_seen


# ===========================================================================
# GET /observations/<id_capture>/<id_individual>  (get_observation)
# ===========================================================================


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestGetObservation:
    def test_unauthenticated_returns_401(self, observation):
        r = self.client.get(
            url_for(
                "individuals.get_observation",
                id_capture=observation.id_capture,
                id_individual=observation.id_individual,
            )
        )
        assert r.status_code == 401

    def test_forbidden_without_rights(self, users, observation):
        set_logged_user(self.client, users["noright_user"])
        r = self.client.get(
            url_for(
                "individuals.get_observation",
                id_capture=observation.id_capture,
                id_individual=observation.id_individual,
            )
        )
        assert r.status_code == 403

    def test_not_found_returns_404(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(
            url_for("individuals.get_observation", id_capture=-1, id_individual=-1)
        )
        assert r.status_code == 404

    def test_not_found_returns_structured_error(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(
            url_for("individuals.get_observation", id_capture=-1, id_individual=-1)
        )
        payload = r.get_json()
        assert payload.get("name") == ApiErrorCode.NOT_FOUND
        assert "description" in payload

    def test_out_of_scope_observation_returns_403(self, users, observations):
        """observations[0]'s capture is digitised by admin_user; self_user (scope=1) can't read it."""
        set_logged_user(self.client, users["self_user"])
        r = self.client.get(
            url_for(
                "individuals.get_observation",
                id_capture=observations[0].id_capture,
                id_individual=observations[0].id_individual,
            )
        )
        assert r.status_code == 403

    def test_returns_200_for_existing_observation(self, users, observation):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(
            url_for(
                "individuals.get_observation",
                id_capture=observation.id_capture,
                id_individual=observation.id_individual,
            )
        )
        assert r.status_code == 200

    def test_payload_contains_expected_fields(self, users, observation):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(
            url_for(
                "individuals.get_observation",
                id_capture=observation.id_capture,
                id_individual=observation.id_individual,
            )
        )
        payload = r.get_json()
        missing = EXPECTED_FIELDS - payload.keys()
        assert not missing, f"Missing fields in payload: {missing}"


# ===========================================================================
# POST /observations  (create_observation)
# ===========================================================================


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestCreateObservation:
    def _payload(self, capture, individual):
        return {
            "id_capture": capture.id_capture,
            "id_individual": individual.id_individual,
            "additional_data": {"weight": 42},
        }

    def test_unauthenticated_returns_401(self, capture, individual):
        r = self.client.post(
            url_for("individuals.create_observation"), json=self._payload(capture, individual)
        )
        assert r.status_code == 401

    def test_forbidden_without_create_permission(self, users, capture, individual):
        set_logged_user(self.client, users["noright_user"])
        r = self.client.post(
            url_for("individuals.create_observation"), json=self._payload(capture, individual)
        )
        assert r.status_code == 403

    def test_forbidden_when_capture_out_of_scope(self, users, captures, individual):
        """captures[0] is digitised by admin_user; self_user (scope=1) can't attach to it."""
        set_logged_user(self.client, users["self_user"])
        r = self.client.post(
            url_for("individuals.create_observation"), json=self._payload(captures[0], individual)
        )
        assert r.status_code == 403

    def test_missing_body_returns_400(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.create_observation"), data="", content_type="application/json"
        )
        assert r.status_code == 400

    def test_unknown_capture_returns_404(self, users, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.create_observation"),
            json={"id_capture": -1, "id_individual": individual.id_individual},
        )
        assert r.status_code == 404

    def test_returns_201_with_valid_payload(self, users, capture, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.create_observation"), json=self._payload(capture, individual)
        )
        assert r.status_code == 201

    def test_response_reflects_payload(self, users, capture, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.create_observation"), json=self._payload(capture, individual)
        )
        data = r.get_json()
        assert data["id_capture"] == capture.id_capture
        assert data["id_individual"] == individual.id_individual
        assert data["additional_data"] == {"weight": 42}
        assert data["individual"]["id_individual"] == individual.id_individual

    def test_duplicate_link_returns_400(self, users, observation):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.create_observation"),
            json={
                "id_capture": observation.id_capture,
                "id_individual": observation.id_individual,
            },
        )
        assert r.status_code == 400

    def test_unknown_individual_returns_400(self, users, capture):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.create_observation"),
            json={"id_capture": capture.id_capture, "id_individual": -1},
        )
        assert r.status_code == 400

    def test_forbidden_for_self_user_even_on_own_capture(self, users, captures, individual):
        """self_user has U/D on INDIVIDUALS but not C (see
        test_forbidden_for_user_without_create_action in test_routes_captures.py),
        so it can't create observations even on captures[1] which it digitised."""
        set_logged_user(self.client, users["self_user"])
        r = self.client.post(
            url_for("individuals.create_observation"), json=self._payload(captures[1], individual)
        )
        assert r.status_code == 403


# ===========================================================================
# PATCH /observations/<id_capture>/<id_individual>  (update_observation)
# ===========================================================================


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestUpdateObservation:
    def test_unauthenticated_returns_401(self, observation):
        r = self.client.patch(
            url_for(
                "individuals.update_observation",
                id_capture=observation.id_capture,
                id_individual=observation.id_individual,
            ),
            json={"additional_data": {"weight": 99}},
        )
        assert r.status_code == 401

    def test_forbidden_without_update_permission(self, users, observation):
        set_logged_user(self.client, users["noright_user"])
        r = self.client.patch(
            url_for(
                "individuals.update_observation",
                id_capture=observation.id_capture,
                id_individual=observation.id_individual,
            ),
            json={"additional_data": {"weight": 99}},
        )
        assert r.status_code == 403

    def test_forbidden_without_scope_permission(self, users, observations):
        """observations[0]'s capture is digitised by admin_user; self_user can't edit it."""
        set_logged_user(self.client, users["self_user"])
        r = self.client.patch(
            url_for(
                "individuals.update_observation",
                id_capture=observations[0].id_capture,
                id_individual=observations[0].id_individual,
            ),
            json={"additional_data": {"weight": 99}},
        )
        assert r.status_code == 403

    def test_not_found_returns_404(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.patch(
            url_for("individuals.update_observation", id_capture=-1, id_individual=-1),
            json={"additional_data": {"weight": 99}},
        )
        assert r.status_code == 404

    def test_not_found_returns_structured_error(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.patch(
            url_for("individuals.update_observation", id_capture=-1, id_individual=-1),
            json={"additional_data": {"weight": 99}},
        )
        payload = r.get_json()
        assert payload.get("name") == ApiErrorCode.NOT_FOUND
        assert "description" in payload

    def test_missing_body_returns_400(self, users, observation):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.patch(
            url_for(
                "individuals.update_observation",
                id_capture=observation.id_capture,
                id_individual=observation.id_individual,
            ),
            data="",
            content_type="application/json",
        )
        assert r.status_code == 400

    def test_returns_200_with_valid_payload(self, users, observation):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.patch(
            url_for(
                "individuals.update_observation",
                id_capture=observation.id_capture,
                id_individual=observation.id_individual,
            ),
            json={"additional_data": {"weight": 99}},
        )
        assert r.status_code == 200

    def test_response_reflects_updated_fields(self, users, observation):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.patch(
            url_for(
                "individuals.update_observation",
                id_capture=observation.id_capture,
                id_individual=observation.id_individual,
            ),
            json={"additional_data": {"weight": 99}},
        )
        assert r.get_json()["additional_data"] == {"weight": 99}

    def test_own_observation_can_be_updated_by_self_user(self, users, observations):
        """observations[1]'s capture is digitised by self_user."""
        set_logged_user(self.client, users["self_user"])
        r = self.client.patch(
            url_for(
                "individuals.update_observation",
                id_capture=observations[1].id_capture,
                id_individual=observations[1].id_individual,
            ),
            json={"additional_data": {"weight": 99}},
        )
        assert r.status_code == 200


# ===========================================================================
# DELETE /observations/<id_capture>/<id_individual>  (delete_observation)
# ===========================================================================


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestDeleteObservation:
    def test_unauthenticated_returns_401(self, observation):
        r = self.client.delete(
            url_for(
                "individuals.delete_observation",
                id_capture=observation.id_capture,
                id_individual=observation.id_individual,
            )
        )
        assert r.status_code == 401

    def test_forbidden_without_delete_permission(self, users, observation):
        set_logged_user(self.client, users["noright_user"])
        r = self.client.delete(
            url_for(
                "individuals.delete_observation",
                id_capture=observation.id_capture,
                id_individual=observation.id_individual,
            )
        )
        assert r.status_code == 403

    def test_forbidden_without_scope_permission(self, users, observations):
        """observations[0]'s capture is digitised by admin_user; self_user can't delete it."""
        set_logged_user(self.client, users["self_user"])
        r = self.client.delete(
            url_for(
                "individuals.delete_observation",
                id_capture=observations[0].id_capture,
                id_individual=observations[0].id_individual,
            )
        )
        assert r.status_code == 403

    def test_not_found_returns_404(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.delete(
            url_for("individuals.delete_observation", id_capture=-1, id_individual=-1)
        )
        assert r.status_code == 404

    def test_not_found_returns_structured_error(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.delete(
            url_for("individuals.delete_observation", id_capture=-1, id_individual=-1)
        )
        payload = r.get_json()
        assert payload.get("name") == ApiErrorCode.NOT_FOUND
        assert "description" in payload

    def test_returns_204_for_existing_observation(self, users, observation):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.delete(
            url_for(
                "individuals.delete_observation",
                id_capture=observation.id_capture,
                id_individual=observation.id_individual,
            )
        )
        assert r.status_code == 204

    def test_response_body_is_empty(self, users, observation):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.delete(
            url_for(
                "individuals.delete_observation",
                id_capture=observation.id_capture,
                id_individual=observation.id_individual,
            )
        )
        assert r.data == b""

    def test_observation_no_longer_exists_after_delete(self, users, observation):
        id_capture, id_individual = observation.id_capture, observation.id_individual
        set_logged_user(self.client, users["admin_user"])
        self.client.delete(
            url_for(
                "individuals.delete_observation",
                id_capture=id_capture,
                id_individual=id_individual,
            )
        )
        r = self.client.get(
            url_for(
                "individuals.get_observation", id_capture=id_capture, id_individual=id_individual
            )
        )
        assert r.status_code == 404

    def test_own_observation_can_be_deleted_by_self_user(self, users, observations):
        """observations[1]'s capture is digitised by self_user."""
        set_logged_user(self.client, users["self_user"])
        r = self.client.delete(
            url_for(
                "individuals.delete_observation",
                id_capture=observations[1].id_capture,
                id_individual=observations[1].id_individual,
            )
        )
        assert r.status_code == 204
