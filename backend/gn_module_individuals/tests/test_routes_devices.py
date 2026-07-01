import pytest
from flask import url_for, g

from pypnusershub.tests.utils import set_logged_user

from gn_module_individuals.schemas import TrackingDevicesDetailSchema, TrackingDevicesWriteSchema
from gn_module_individuals.utils.errors import DevicesErrorCode

# ===========================================================================
# GET /devices  (list_devices)
# ===========================================================================


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestListDevices:

    # Test unauthenticated first (no auth token set yet for the class client)
    def test_unauthenticated_returns_401(self):
        r = self.client.get(url_for("individuals.list_devices"))
        assert r.status_code == 401

    def test_forbidden_without_rights(self, users):
        set_logged_user(self.client, users["noright_user"])
        r = self.client.get(url_for("individuals.list_devices"))
        assert r.status_code == 403

    def test_without_pagination_returns_list(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_devices"))
        assert r.status_code == 200
        assert isinstance(r.get_json(), list)

    def test_with_pagination_returns_paginated_object(self, users, devices):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_devices", page=1, per_page=2))
        assert r.status_code == 200
        payload = r.get_json()
        for key in ("items", "page", "per_page", "total", "pages", "has_next", "has_prev"):
            assert key in payload, f"Clé manquante dans la réponse paginée : {key}"
        assert isinstance(payload["items"], list)

    def test_pagination_page_and_per_page(self, users, devices):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_devices", page=1, per_page=1))
        payload = r.get_json()
        assert len(payload["items"]) == 1
        assert payload["per_page"] == 1
        assert payload["page"] == 1

    EXPECTED_FIELDS = {
        "id_tracking_device",
        "provider_name",
        "provider_device_id",
        "id_nomenclature_device_type",
        "nomenclature_device_type_name",
        "digitiser_name",
        "referer_name",
        "last_individual_equipped_name",
        "meta_create_date",
    }

    def test_item_contains_expected_fields(self, users, device):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_devices", page=1, per_page=1))
        item = r.get_json()["items"][0]
        missing = self.EXPECTED_FIELDS - item.keys()
        assert not missing, f"Champs manquants dans l'item : {missing}"

    def test_filter_by_provider_name_no_match(self, users, devices):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_devices", provider_name="__no_match_xyz__"))
        assert r.get_json() == []

    def test_filter_by_id_referer_no_match(self, users, devices):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_devices", id_referer=-1))
        assert r.get_json() == []

    def test_filter_by_id_nomenclature_device_type_no_match(self, users, devices):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_devices", id_nomenclature_device_type=-1))
        assert r.get_json() == []

    def test_filter_by_cd_nom_no_match(self, users, devices):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_devices", cd_nom=-1))
        assert r.get_json() == []


# ===========================================================================
# GET /devices/<id>  (device)
# ===========================================================================


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestGetDevice:

    def test_unauthenticated_returns_401(self, device):
        r = self.client.get(
            url_for("individuals.device", id_tracking_device=device.id_tracking_device)
        )
        assert r.status_code == 401

    def test_forbidden_without_rights(self, users, device):
        set_logged_user(self.client, users["noright_user"])
        r = self.client.get(
            url_for("individuals.device", id_tracking_device=device.id_tracking_device)
        )
        assert r.status_code == 403

    def test_not_found_returns_404(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.device", id_tracking_device=-1))
        assert r.status_code == 404

    def test_not_found_returns_structured_error(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.device", id_tracking_device=-1))
        payload = r.get_json()
        assert payload.get("name") == DevicesErrorCode.DEVICE_NOT_FOUND
        assert "description" in payload

    def test_returns_200_for_existing_device(self, users, device):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(
            url_for("individuals.device", id_tracking_device=device.id_tracking_device)
        )
        assert r.status_code == 200
        data = r.get_json()
        expected_keys = set(TrackingDevicesDetailSchema().fields.keys())
        missing = expected_keys - data.keys()
        assert not missing, f"Champs manquants dans la réponse : {missing}"

    def test_payload_id_matches(self, users, device):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(
            url_for("individuals.device", id_tracking_device=device.id_tracking_device)
        )
        assert r.get_json()["id_tracking_device"] == device.id_tracking_device

    def test_detail_includes_deployments(self, users, device_with_deployment):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(
            url_for(
                "individuals.device",
                id_tracking_device=device_with_deployment.id_tracking_device,
            )
        )
        assert r.status_code == 200
        data = r.get_json()
        assert isinstance(data["deployments"], list)
        assert len(data["deployments"]) > 0
        assert data["deployments"][0]["individual_name"] is not None


# ===========================================================================
# POST /devices  (create_device)
# ===========================================================================


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestCreateDevice:

    VALID_PAYLOAD = {
        "provider_name": "Ornitela",
        "provider_device_id": "TEST_POST_001",
    }

    def test_unauthenticated_returns_401(self):
        r = self.client.post(url_for("individuals.create_device"), json=self.VALID_PAYLOAD)
        assert r.status_code == 401

    def test_forbidden_without_create_permission(self, users):
        set_logged_user(self.client, users["noright_user"])
        r = self.client.post(url_for("individuals.create_device"), json=self.VALID_PAYLOAD)
        assert r.status_code == 403

    def test_returns_201_with_valid_payload(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(url_for("individuals.create_device"), json=self.VALID_PAYLOAD)
        assert r.status_code == 201

    def test_response_contains_id(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(url_for("individuals.create_device"), json=self.VALID_PAYLOAD)
        payload = r.get_json()
        assert "id_tracking_device" in payload
        assert payload["id_tracking_device"] is not None

    def test_response_validates_schema(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(url_for("individuals.create_device"), json=self.VALID_PAYLOAD)
        assert r.status_code == 201
        data = r.get_json()
        expected_keys = set(TrackingDevicesWriteSchema().fields.keys())
        missing = expected_keys - data.keys()
        assert not missing, f"Champs manquants dans la réponse : {missing}"

    def test_digitiser_is_set_from_authenticated_user(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(url_for("individuals.create_device"), json=self.VALID_PAYLOAD)
        device_id = r.get_json()["id_tracking_device"]
        detail = self.client.get(
            url_for("individuals.device", id_tracking_device=device_id)
        ).get_json()
        assert detail["id_digitiser"] == users["admin_user"].id_role

    def test_empty_provider_name_returns_400(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.create_device"),
            json={"provider_name": "   ", "provider_device_id": "X"},
        )
        assert r.status_code == 400

    def test_empty_provider_device_id_returns_400(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.create_device"),
            json={"provider_name": "Ornitela", "provider_device_id": ""},
        )
        assert r.status_code == 400

    def test_invalid_nomenclature_returns_400(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.create_device"),
            json={**self.VALID_PAYLOAD, "id_nomenclature_device_type": -999},
        )
        assert r.status_code == 400

    def test_invalid_referer_returns_400(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.create_device"),
            json={**self.VALID_PAYLOAD, "id_referer": -999},
        )
        assert r.status_code == 400

    def test_computed_fields_in_payload_are_ignored(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.create_device"),
            json={
                **self.VALID_PAYLOAD,
                "nomenclature_device_type_name": "Balise GPS",
                "digitiser_name": "Test Agent",
                "referer_name": "Test Agent",
                "last_individual_equipped_name": None,
            },
        )
        assert r.status_code == 201

    def test_missing_body_returns_structured_error(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.create_device"),
            data="",
            content_type="application/json",
        )
        assert r.status_code == 400
        payload = r.get_json()
        assert payload.get("name") == DevicesErrorCode.MISSING_JSON_BODY
        assert "description" in payload

    def test_validation_error_returns_structured_error(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.create_device"),
            json={"provider_name": "   ", "provider_device_id": "X"},
        )
        assert r.status_code == 400
        payload = r.get_json()
        assert payload.get("name") == DevicesErrorCode.VALIDATION_ERROR
        assert "description" in payload


# ===========================================================================
# PUT /devices/<id>  (update_device)
# ===========================================================================


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestUpdateDevice:

    def test_unauthenticated_returns_401(self, device):
        r = self.client.put(
            url_for("individuals.update_device", id_tracking_device=device.id_tracking_device),
            json={"provider_name": "X", "provider_device_id": "Y"},
        )
        assert r.status_code == 401

    def test_forbidden_without_update_permission(self, users, device):
        set_logged_user(self.client, users["noright_user"])
        r = self.client.put(
            url_for("individuals.update_device", id_tracking_device=device.id_tracking_device),
            json={"provider_name": "X", "provider_device_id": "Y"},
        )
        assert r.status_code == 403

    def test_forbidden_without_scope_permission(self, users, devices):
        # self_user a le droit U mais scope=1 (ses données uniquement).
        # devices[0] appartient à admin_user (digitiseur ET référent) → 403
        set_logged_user(self.client, users["self_user"])
        r = self.client.put(
            url_for(
                "individuals.update_device",
                id_tracking_device=devices[0].id_tracking_device,
            ),
            json={"provider_name": "X", "provider_device_id": "Y"},
        )
        assert r.status_code == 403

    def test_not_found_returns_404(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.put(
            url_for("individuals.update_device", id_tracking_device=-1),
            json={"provider_name": "X", "provider_device_id": "Y"},
        )
        assert r.status_code == 404

    def test_not_found_returns_structured_error(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.put(
            url_for("individuals.update_device", id_tracking_device=-1),
            json={"provider_name": "X", "provider_device_id": "Y"},
        )
        payload = r.get_json()
        assert payload.get("name") == DevicesErrorCode.DEVICE_NOT_FOUND
        assert "description" in payload

    def test_forbidden_scope_returns_structured_error(self, users, devices):
        set_logged_user(self.client, users["self_user"])
        r = self.client.put(
            url_for(
                "individuals.update_device",
                id_tracking_device=devices[0].id_tracking_device,
            ),
            json={"provider_name": "X", "provider_device_id": "Y"},
        )
        assert r.status_code == 403
        payload = r.get_json()
        assert payload.get("name") == DevicesErrorCode.INSUFFICIENT_PERMISSIONS
        assert "description" in payload

    def test_returns_200_with_valid_payload(self, users, device):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.put(
            url_for("individuals.update_device", id_tracking_device=device.id_tracking_device),
            json={"provider_name": "Ornitela Updated", "provider_device_id": "UPD_001"},
        )
        assert r.status_code == 200

    def test_response_validates_schema(self, users, device):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.put(
            url_for("individuals.update_device", id_tracking_device=device.id_tracking_device),
            json={"provider_name": "X", "provider_device_id": "Y"},
        )
        assert r.status_code == 200
        data = r.get_json()
        expected_keys = set(TrackingDevicesWriteSchema().fields.keys())
        missing = expected_keys - data.keys()
        assert not missing, f"Champs manquants dans la réponse : {missing}"

    def test_response_reflects_updated_fields(self, users, device):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.put(
            url_for("individuals.update_device", id_tracking_device=device.id_tracking_device),
            json={"provider_name": "NewProvider", "provider_device_id": "UPD_002"},
        )
        data = r.get_json()
        assert data["provider_name"] == "NewProvider"
        assert data["provider_device_id"] == "UPD_002"

    def test_digitiser_is_set_from_authenticated_user(self, users, device):
        set_logged_user(self.client, users["admin_user"])
        self.client.put(
            url_for("individuals.update_device", id_tracking_device=device.id_tracking_device),
            json={"provider_name": "X", "provider_device_id": "Y"},
        )
        detail = self.client.get(
            url_for("individuals.device", id_tracking_device=device.id_tracking_device)
        ).get_json()
        assert detail["id_digitiser"] == users["admin_user"].id_role

    def test_computed_fields_in_payload_are_ignored(self, users, device):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.put(
            url_for("individuals.update_device", id_tracking_device=device.id_tracking_device),
            json={
                "provider_name": "X",
                "provider_device_id": "Y",
                "nomenclature_device_type_name": "Balise GPS",
                "digitiser_name": "Test Agent",
            },
        )
        assert r.status_code == 200

    def test_empty_provider_name_returns_400(self, users, device):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.put(
            url_for("individuals.update_device", id_tracking_device=device.id_tracking_device),
            json={"provider_name": "", "provider_device_id": "X"},
        )
        assert r.status_code == 400

    def test_invalid_nomenclature_returns_400(self, users, device):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.put(
            url_for("individuals.update_device", id_tracking_device=device.id_tracking_device),
            json={
                "provider_name": "X",
                "provider_device_id": "Y",
                "id_nomenclature_device_type": -999,
            },
        )
        assert r.status_code == 400


# ===========================================================================
# DELETE /devices/<id>  (delete_device)
# ===========================================================================


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestDeleteDevice:

    def test_unauthenticated_returns_401(self, device):
        r = self.client.delete(
            url_for("individuals.delete_device", id_tracking_device=device.id_tracking_device)
        )
        assert r.status_code == 401

    def test_forbidden_without_delete_permission(self, users, device):
        set_logged_user(self.client, users["noright_user"])
        r = self.client.delete(
            url_for("individuals.delete_device", id_tracking_device=device.id_tracking_device)
        )
        assert r.status_code == 403

    def test_not_found_returns_404(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.delete(url_for("individuals.delete_device", id_tracking_device=-1))
        assert r.status_code == 404

    def test_returns_204_for_existing_device(self, users, device):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.delete(
            url_for("individuals.delete_device", id_tracking_device=device.id_tracking_device)
        )
        assert r.status_code == 204

    def test_response_body_is_empty(self, users, device):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.delete(
            url_for("individuals.delete_device", id_tracking_device=device.id_tracking_device)
        )
        assert r.data == b""

    def test_device_no_longer_exists_after_delete(self, users, device):
        device_id = device.id_tracking_device
        set_logged_user(self.client, users["admin_user"])
        self.client.delete(url_for("individuals.delete_device", id_tracking_device=device_id))
        r = self.client.get(url_for("individuals.device", id_tracking_device=device_id))
        assert r.status_code == 404

    def test_conflict_if_device_has_deployments(self, users, device_with_deployment):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.delete(
            url_for(
                "individuals.delete_device",
                id_tracking_device=device_with_deployment.id_tracking_device,
            )
        )
        assert r.status_code == 409

    def test_not_found_returns_structured_error(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.delete(url_for("individuals.delete_device", id_tracking_device=-1))
        payload = r.get_json()
        assert payload.get("name") == DevicesErrorCode.DEVICE_NOT_FOUND
        assert "description" in payload

    def test_conflict_returns_structured_error(self, users, device_with_deployment):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.delete(
            url_for(
                "individuals.delete_device",
                id_tracking_device=device_with_deployment.id_tracking_device,
            )
        )
        payload = r.get_json()
        assert payload.get("name") == DevicesErrorCode.DEVICE_HAS_DEPLOYMENTS
        assert "description" in payload
        assert payload.get("params", {}).get("id") == device_with_deployment.id_tracking_device
        assert payload.get("params", {}).get("nb") == 1
