import pytest
from flask import url_for

from pypnusershub.tests.utils import set_logged_user
from geonature.tests.utils import get_id_nomenclature
from geonature.utils.env import db

from gn_module_individuals.schemas import DeploymentWriteSchema
from gn_module_individuals.models import IndividualDeployments
from gn_module_individuals.utils.errors import ApiErrorCode


def _valid_payload(individual, **overrides):
    payload = {
        "id_individual": individual.id_individual,
        "id_nomenclature_deployment_type": get_id_nomenclature(
            nomenclature_type_mnemonique="TYPE_MARQUAGE", cd_nomenclature="4"
        ),
        "id_nomenclature_deployment_location": get_id_nomenclature(
            nomenclature_type_mnemonique="LOC_MARQUAGE", cd_nomenclature="3"
        ),
        "install_date": "2024-01-01",
    }
    payload.update(overrides)
    return payload


# ===========================================================================
# POST /deployments  (create_deployment)
# ===========================================================================


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestCreateDeployment:

    def test_unauthenticated_returns_401(self, individual):
        r = self.client.post(
            url_for("individuals.create_deployment"), json=_valid_payload(individual)
        )
        assert r.status_code == 401

    def test_forbidden_without_create_permission(self, users, individual):
        set_logged_user(self.client, users["noright_user"])
        r = self.client.post(
            url_for("individuals.create_deployment"), json=_valid_payload(individual)
        )
        assert r.status_code == 403

    def test_returns_201_with_valid_payload(self, users, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.create_deployment"), json=_valid_payload(individual)
        )
        assert r.status_code == 201

    def test_response_contains_id(self, users, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.create_deployment"), json=_valid_payload(individual)
        )
        payload = r.get_json()
        assert "id_deployment" in payload
        assert payload["id_deployment"] is not None

    def test_response_validates_schema(self, users, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.create_deployment"), json=_valid_payload(individual)
        )
        assert r.status_code == 201
        data = r.get_json()
        expected_keys = set(DeploymentWriteSchema().fields.keys())
        missing = expected_keys - data.keys()
        assert not missing, f"Champs manquants dans la réponse : {missing}"

    def test_digitiser_is_set_from_authenticated_user(self, users, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.create_deployment"), json=_valid_payload(individual)
        )
        assert r.get_json()["id_digitiser"] == users["admin_user"].id_role

    def test_response_reflects_submitted_fields(self, users, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.create_deployment"),
            json=_valid_payload(individual, marking_code="MC-001"),
        )
        data = r.get_json()
        assert data["id_individual"] == individual.id_individual
        assert data["marking_code"] == "MC-001"

    def test_missing_body_returns_structured_error(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.create_deployment"),
            data="",
            content_type="application/json",
        )
        assert r.status_code == 400
        payload = r.get_json()
        assert payload.get("name") == ApiErrorCode.MISSING_JSON_BODY
        assert "description" in payload

    def test_missing_required_field_returns_400(self, users, individual):
        set_logged_user(self.client, users["admin_user"])
        payload = _valid_payload(individual)
        del payload["id_individual"]
        r = self.client.post(url_for("individuals.create_deployment"), json=payload)
        assert r.status_code == 400

    def test_validation_error_returns_structured_error(self, users, individual):
        set_logged_user(self.client, users["admin_user"])
        payload = _valid_payload(individual)
        del payload["id_individual"]
        r = self.client.post(url_for("individuals.create_deployment"), json=payload)
        assert r.status_code == 400
        body = r.get_json()
        assert body.get("name") == ApiErrorCode.VALIDATION_ERROR
        assert "description" in body

    def test_invalid_individual_returns_400(self, users, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.create_deployment"),
            json=_valid_payload(individual, id_individual=-999),
        )
        assert r.status_code == 400

    def test_invalid_deployment_type_nomenclature_returns_400(self, users, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.create_deployment"),
            json=_valid_payload(individual, id_nomenclature_deployment_type=-999),
        )
        assert r.status_code == 400

    def test_invalid_deployment_location_nomenclature_returns_400(self, users, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.create_deployment"),
            json=_valid_payload(individual, id_nomenclature_deployment_location=-999),
        )
        assert r.status_code == 400

    def test_invalid_tracking_device_returns_400(self, users, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.create_deployment"),
            json=_valid_payload(individual, id_tracking_device=-999),
        )
        assert r.status_code == 400

    def test_removal_date_before_install_date_returns_400(self, users, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.create_deployment"),
            json=_valid_payload(individual, removal_date="2023-12-31"),
        )
        assert r.status_code == 400

    def test_computed_fields_in_payload_are_ignored(self, users, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.create_deployment"),
            json=_valid_payload(
                individual,
                id_deployment=999999,
                id_digitiser=-1,
                individual_name="Should be ignored",
                deployment_type_name="Should be ignored",
                deployment_location_name="Should be ignored",
            ),
        )
        assert r.status_code == 201
        data = r.get_json()
        assert data["id_deployment"] != 999999
        assert data["id_digitiser"] == users["admin_user"].id_role


# ===========================================================================
# PUT /deployments/<id>  (update_deployment)
# ===========================================================================


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestUpdateDeployment:

    def test_unauthenticated_returns_401(self, deployment, individual):
        r = self.client.put(
            url_for("individuals.update_deployment", id_deployment=deployment.id_deployment),
            json=_valid_payload(individual),
        )
        assert r.status_code == 401

    def test_forbidden_without_update_permission(self, users, deployment, individual):
        set_logged_user(self.client, users["noright_user"])
        r = self.client.put(
            url_for("individuals.update_deployment", id_deployment=deployment.id_deployment),
            json=_valid_payload(individual),
        )
        assert r.status_code == 403

    def test_forbidden_without_scope_permission(self, users, deployment, individual):
        # deployment is digitised by admin_user; self_user only has scope=1 (its own data) -> 403
        set_logged_user(self.client, users["self_user"])
        r = self.client.put(
            url_for("individuals.update_deployment", id_deployment=deployment.id_deployment),
            json=_valid_payload(individual),
        )
        assert r.status_code == 403

    def test_allowed_within_own_scope(self, users, deployment_by_self, individual):
        set_logged_user(self.client, users["self_user"])
        r = self.client.put(
            url_for(
                "individuals.update_deployment", id_deployment=deployment_by_self.id_deployment
            ),
            json=_valid_payload(individual),
        )
        assert r.status_code == 200

    def test_not_found_returns_404(self, users, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.put(
            url_for("individuals.update_deployment", id_deployment=-1),
            json=_valid_payload(individual),
        )
        assert r.status_code == 404

    def test_not_found_returns_structured_error(self, users, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.put(
            url_for("individuals.update_deployment", id_deployment=-1),
            json=_valid_payload(individual),
        )
        payload = r.get_json()
        assert payload.get("name") == ApiErrorCode.NOT_FOUND
        assert "description" in payload

    def test_forbidden_scope_returns_structured_error(self, users, deployment, individual):
        set_logged_user(self.client, users["self_user"])
        r = self.client.put(
            url_for("individuals.update_deployment", id_deployment=deployment.id_deployment),
            json=_valid_payload(individual),
        )
        assert r.status_code == 403
        payload = r.get_json()
        assert payload.get("name") == ApiErrorCode.INSUFFICIENT_PERMISSIONS
        assert "description" in payload

    def test_missing_body_returns_structured_error(self, users, deployment):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.put(
            url_for("individuals.update_deployment", id_deployment=deployment.id_deployment),
            data="",
            content_type="application/json",
        )
        assert r.status_code == 400
        payload = r.get_json()
        assert payload.get("name") == ApiErrorCode.MISSING_JSON_BODY
        assert "description" in payload

    def test_returns_200_with_valid_payload(self, users, deployment, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.put(
            url_for("individuals.update_deployment", id_deployment=deployment.id_deployment),
            json=_valid_payload(individual, install_date="2024-03-01", marking_code="MC-UPD"),
        )
        assert r.status_code == 200

    def test_response_reflects_updated_fields(self, users, deployment, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.put(
            url_for("individuals.update_deployment", id_deployment=deployment.id_deployment),
            json=_valid_payload(individual, install_date="2024-03-01", marking_code="MC-UPD"),
        )
        data = r.get_json()
        assert data["install_date"] == "2024-03-01"
        assert data["marking_code"] == "MC-UPD"

    def test_digitiser_is_set_from_authenticated_user(self, users, deployment, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.put(
            url_for("individuals.update_deployment", id_deployment=deployment.id_deployment),
            json=_valid_payload(individual),
        )
        assert r.get_json()["id_digitiser"] == users["admin_user"].id_role

    def test_computed_fields_in_payload_are_ignored(self, users, deployment, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.put(
            url_for("individuals.update_deployment", id_deployment=deployment.id_deployment),
            json=_valid_payload(
                individual,
                id_digitiser=-1,
                individual_name="Should be ignored",
                deployment_type_name="Should be ignored",
            ),
        )
        assert r.status_code == 200

    def test_invalid_nomenclature_returns_400(self, users, deployment, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.put(
            url_for("individuals.update_deployment", id_deployment=deployment.id_deployment),
            json=_valid_payload(individual, id_nomenclature_deployment_type=-999),
        )
        assert r.status_code == 400

    def test_removal_date_before_install_date_returns_400(self, users, deployment, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.put(
            url_for("individuals.update_deployment", id_deployment=deployment.id_deployment),
            json=_valid_payload(
                individual,
                install_date="2024-03-01",
                removal_date="2024-01-01",
            ),
        )
        assert r.status_code == 400


# ===========================================================================
# DELETE /deployments/<id>  (delete_deployment)
# ===========================================================================


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestDeleteDeployment:

    def test_unauthenticated_returns_401(self, deployment):
        r = self.client.delete(
            url_for("individuals.delete_deployment", id_deployment=deployment.id_deployment)
        )
        assert r.status_code == 401

    def test_forbidden_without_delete_permission(self, users, deployment):
        set_logged_user(self.client, users["noright_user"])
        r = self.client.delete(
            url_for("individuals.delete_deployment", id_deployment=deployment.id_deployment)
        )
        assert r.status_code == 403

    def test_forbidden_without_scope_permission(self, users, deployment):
        # deployment is digitised by admin_user; self_user only has scope=1 -> 403
        set_logged_user(self.client, users["self_user"])
        r = self.client.delete(
            url_for("individuals.delete_deployment", id_deployment=deployment.id_deployment)
        )
        assert r.status_code == 403

    def test_allowed_within_own_scope(self, users, deployment_by_self):
        set_logged_user(self.client, users["self_user"])
        r = self.client.delete(
            url_for(
                "individuals.delete_deployment", id_deployment=deployment_by_self.id_deployment
            )
        )
        assert r.status_code == 204

    def test_forbidden_scope_returns_structured_error(self, users, deployment):
        set_logged_user(self.client, users["self_user"])
        r = self.client.delete(
            url_for("individuals.delete_deployment", id_deployment=deployment.id_deployment)
        )
        assert r.status_code == 403
        payload = r.get_json()
        assert payload.get("name") == ApiErrorCode.INSUFFICIENT_PERMISSIONS
        assert "description" in payload

    def test_not_found_returns_404(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.delete(url_for("individuals.delete_deployment", id_deployment=-1))
        assert r.status_code == 404

    def test_not_found_returns_structured_error(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.delete(url_for("individuals.delete_deployment", id_deployment=-1))
        payload = r.get_json()
        assert payload.get("name") == ApiErrorCode.NOT_FOUND
        assert "description" in payload

    def test_returns_204_for_existing_deployment(self, users, deployment):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.delete(
            url_for("individuals.delete_deployment", id_deployment=deployment.id_deployment)
        )
        assert r.status_code == 204

    def test_response_body_is_empty(self, users, deployment):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.delete(
            url_for("individuals.delete_deployment", id_deployment=deployment.id_deployment)
        )
        assert r.data == b""

    def test_deployment_no_longer_exists_after_delete(self, users, deployment):
        deployment_id = deployment.id_deployment
        set_logged_user(self.client, users["admin_user"])
        self.client.delete(url_for("individuals.delete_deployment", id_deployment=deployment_id))
        assert db.session.get(IndividualDeployments, deployment_id) is None
