import pytest
from flask import url_for

from pypnusershub.tests.utils import set_logged_user

from gn_module_individuals.utils.errors import ApiErrorCode

VALID_PAYLOAD = {
    "date": "2023-01-01T00:00:00",
    "geom_local": {"type": "Point", "coordinates": [6.0, 45.0]},
}

# ===========================================================================
# GET /captures  (list_captures)
# ===========================================================================


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestListCaptures:
    def test_unauthenticated_returns_401(self):
        r = self.client.get(url_for("individuals.list_captures"))
        assert r.status_code == 401

    def test_forbidden_without_rights(self, users):
        set_logged_user(self.client, users["noright_user"])
        r = self.client.get(url_for("individuals.list_captures"))
        assert r.status_code == 403

    def test_returns_200_with_list(self, users, captures):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_captures"))
        assert r.status_code == 200
        assert isinstance(r.get_json(), list)

    EXPECTED_FIELDS = {
        "id_capture",
        "id_digitiser",
        "id_nomenclature_capture_protocol",
        "nomenclature_capture_protocol",
        "comment",
        "date",
        "geom_local",
        "additional_data",
        "meta_create_date",
        "meta_update_date",
        "cruved",
    }

    def test_item_contains_expected_fields(self, users, capture):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_captures"))
        item = next(i for i in r.get_json() if i["id_capture"] == capture.id_capture)
        missing = self.EXPECTED_FIELDS - item.keys()
        assert not missing, f"Missing fields in item: {missing}"

    def test_list_is_not_scoped(self, users, captures):
        """Regression/documentation test: unlike capture_geometry and
        get_capture_by_id, list_captures does not call Capture.filter_by_scope,
        so a scope=1 user still sees captures digitised by other users."""
        set_logged_user(self.client, users["self_user"])
        r = self.client.get(url_for("individuals.list_captures"))
        assert r.status_code == 200
        ids = {item["id_capture"] for item in r.get_json()}
        assert {c.id_capture for c in captures} <= ids

    def test_item_cruved_reflects_instance_permission(self, users, captures):
        """captures[0] is digitised by admin_user, captures[1] by self_user."""
        set_logged_user(self.client, users["self_user"])
        r = self.client.get(url_for("individuals.list_captures"))
        items = {item["id_capture"]: item for item in r.get_json()}
        own_item = items[captures[1].id_capture]
        other_item = items[captures[0].id_capture]
        assert own_item["cruved"]["U"] is True
        assert own_item["cruved"]["D"] is True
        assert other_item["cruved"]["U"] is False
        assert other_item["cruved"]["D"] is False


# ===========================================================================
# GET /captures/geometry  (capture_geometry)
# ===========================================================================


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestCaptureGeometry:
    def test_unauthenticated_returns_401(self):
        r = self.client.get(url_for("individuals.capture_geometry"))
        assert r.status_code == 401

    def test_forbidden_without_rights(self, users):
        set_logged_user(self.client, users["noright_user"])
        r = self.client.get(url_for("individuals.capture_geometry"))
        assert r.status_code == 403

    def test_returns_geojson_feature_collection(self, users, captures):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.capture_geometry"))
        assert r.status_code == 200
        data = r.get_json()
        assert data["type"] == "FeatureCollection"
        assert isinstance(data["features"], list)

    def test_features_have_expected_properties(self, users, capture):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.capture_geometry"))
        feature = next(
            f
            for f in r.get_json()["features"]
            if f["properties"]["id_capture"] == capture.id_capture
        )
        assert feature["type"] == "Feature"
        assert feature["geometry"] is not None
        props = feature["properties"]
        for key in (
            "id_capture",
            "comment",
            "date",
            "additional_data",
            "meta_create_date",
            "meta_update_date",
        ):
            assert key in props

    def test_scope_restricts_to_own_data(self, users, captures):
        """captures[0] is digitised by admin_user, captures[1] by self_user."""
        set_logged_user(self.client, users["self_user"])
        r = self.client.get(url_for("individuals.capture_geometry"))
        assert r.status_code == 200
        ids = {f["properties"]["id_capture"] for f in r.get_json()["features"]}
        assert captures[1].id_capture in ids
        assert captures[0].id_capture not in ids


# ===========================================================================
# GET /captures/<id>  (get_capture_by_id)
# ===========================================================================


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestGetCapture:
    def test_unauthenticated_returns_401(self, capture):
        r = self.client.get(
            url_for("individuals.get_capture_by_id", id_capture=capture.id_capture)
        )
        assert r.status_code == 401

    def test_forbidden_without_rights(self, users, capture):
        set_logged_user(self.client, users["noright_user"])
        r = self.client.get(
            url_for("individuals.get_capture_by_id", id_capture=capture.id_capture)
        )
        assert r.status_code == 403

    def test_not_found_returns_404(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.get_capture_by_id", id_capture=-1))
        assert r.status_code == 404

    def test_not_found_returns_structured_error(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.get_capture_by_id", id_capture=-1))
        payload = r.get_json()
        assert payload.get("name") == ApiErrorCode.NOT_FOUND
        assert "description" in payload

    def test_out_of_scope_capture_returns_403(self, users, captures):
        """captures[0] is digitised by admin_user; self_user (scope=1) can't read it."""
        set_logged_user(self.client, users["self_user"])
        r = self.client.get(
            url_for("individuals.get_capture_by_id", id_capture=captures[0].id_capture)
        )
        assert r.status_code == 403

    def test_returns_200_for_existing_capture(self, users, capture):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(
            url_for("individuals.get_capture_by_id", id_capture=capture.id_capture)
        )
        assert r.status_code == 200

    EXPECTED_FIELDS = {
        "id_capture",
        "id_digitiser",
        "id_nomenclature_capture_protocol",
        "nomenclature_capture_protocol",
        "comment",
        "date",
        "geom_local",
        "additional_data",
        "meta_create_date",
        "meta_update_date",
        "cruved",
    }

    def test_payload_contains_expected_fields(self, users, capture):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(
            url_for("individuals.get_capture_by_id", id_capture=capture.id_capture)
        )
        payload = r.get_json()
        missing = self.EXPECTED_FIELDS - payload.keys()
        assert not missing, f"Missing fields in payload: {missing}"

    def test_payload_id_matches(self, users, capture):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(
            url_for("individuals.get_capture_by_id", id_capture=capture.id_capture)
        )
        assert r.get_json()["id_capture"] == capture.id_capture


# ===========================================================================
# POST /captures  (post_capture)
# ===========================================================================


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestCreateCapture:
    def test_unauthenticated_returns_401(self):
        r = self.client.post(url_for("individuals.post_capture"), json=VALID_PAYLOAD)
        assert r.status_code == 401

    def test_forbidden_without_create_permission(self, users):
        set_logged_user(self.client, users["noright_user"])
        r = self.client.post(url_for("individuals.post_capture"), json=VALID_PAYLOAD)
        assert r.status_code == 403

    def test_forbidden_for_user_without_create_action(self, users):
        """self_user only has U/D on captures, not C."""
        set_logged_user(self.client, users["self_user"])
        r = self.client.post(url_for("individuals.post_capture"), json=VALID_PAYLOAD)
        assert r.status_code == 403

    def test_returns_201_with_valid_payload(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(url_for("individuals.post_capture"), json=VALID_PAYLOAD)
        assert r.status_code == 201

    def test_response_contains_id(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(url_for("individuals.post_capture"), json=VALID_PAYLOAD)
        payload = r.get_json()
        assert "id_capture" in payload
        assert payload["id_capture"] is not None

    def test_digitiser_is_set_from_authenticated_user(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(url_for("individuals.post_capture"), json=VALID_PAYLOAD)
        assert r.get_json()["id_digitiser"] == users["admin_user"].id_role

    def test_response_reflects_payload(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(url_for("individuals.post_capture"), json=VALID_PAYLOAD)
        data = r.get_json()
        assert data["date"] == VALID_PAYLOAD["date"]
        assert data["geom_local"] == VALID_PAYLOAD["geom_local"]

    def test_missing_date_returns_400(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.post_capture"),
            json={"geom_local": VALID_PAYLOAD["geom_local"]},
        )
        assert r.status_code == 400

    def test_missing_geom_returns_500(self, users):
        """Documents current behaviour: geom_local is nullable=False at the DB
        level but not required by CapturesSchema, so an omitted geometry isn't
        caught by validation and instead crashes on commit."""
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.post_capture"),
            json={"date": VALID_PAYLOAD["date"]},
        )
        assert r.status_code == 500

    def test_missing_body_returns_500(self, users):
        """Documents current behaviour: unlike devices/individuals routes,
        post_capture does not check for a missing JSON body before indexing
        into it, so an empty request crashes instead of returning 400."""
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.post_capture"), data="", content_type="application/json"
        )
        assert r.status_code == 500


# ===========================================================================
# PATCH /captures/<id>  (patch_capture)
# ===========================================================================


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestUpdateCapture:
    def test_unauthenticated_returns_401(self, capture):
        r = self.client.patch(
            url_for("individuals.patch_capture", id_capture=capture.id_capture), json=VALID_PAYLOAD
        )
        assert r.status_code == 401

    def test_forbidden_without_update_permission(self, users, capture):
        set_logged_user(self.client, users["noright_user"])
        r = self.client.patch(
            url_for("individuals.patch_capture", id_capture=capture.id_capture), json=VALID_PAYLOAD
        )
        assert r.status_code == 403

    def test_forbidden_without_scope_permission(self, users, captures):
        """captures[0] is digitised by admin_user; self_user (U, scope=1) can't edit it."""
        set_logged_user(self.client, users["self_user"])
        r = self.client.patch(
            url_for("individuals.patch_capture", id_capture=captures[0].id_capture),
            json=VALID_PAYLOAD,
        )
        assert r.status_code == 403

    def test_not_found_returns_404(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.patch(
            url_for("individuals.patch_capture", id_capture=-1), json=VALID_PAYLOAD
        )
        assert r.status_code == 404

    def test_not_found_returns_structured_error(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.patch(
            url_for("individuals.patch_capture", id_capture=-1), json=VALID_PAYLOAD
        )
        payload = r.get_json()
        assert payload.get("name") == ApiErrorCode.NOT_FOUND
        assert "description" in payload

    def test_returns_200_with_valid_payload(self, users, capture):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.patch(
            url_for("individuals.patch_capture", id_capture=capture.id_capture), json=VALID_PAYLOAD
        )
        assert r.status_code == 200

    def test_response_reflects_updated_fields(self, users, capture):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.patch(
            url_for("individuals.patch_capture", id_capture=capture.id_capture),
            json={**VALID_PAYLOAD, "comment": "updated comment"},
        )
        data = r.get_json()
        assert data["comment"] == "updated comment"
        assert data["date"] == VALID_PAYLOAD["date"]

    def test_own_capture_can_be_updated_by_self_user(self, users, captures):
        """captures[1] is digitised by self_user."""
        set_logged_user(self.client, users["self_user"])
        r = self.client.patch(
            url_for("individuals.patch_capture", id_capture=captures[1].id_capture),
            json=VALID_PAYLOAD,
        )
        assert r.status_code == 200


# ===========================================================================
# DELETE /captures/<id>  (delete_capture)
# ===========================================================================


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestDeleteCapture:
    def test_unauthenticated_returns_401(self, capture):
        r = self.client.delete(
            url_for("individuals.delete_capture", id_capture=capture.id_capture)
        )
        assert r.status_code == 401

    def test_forbidden_without_delete_permission(self, users, capture):
        set_logged_user(self.client, users["noright_user"])
        r = self.client.delete(
            url_for("individuals.delete_capture", id_capture=capture.id_capture)
        )
        assert r.status_code == 403

    def test_forbidden_without_scope_permission(self, users, captures):
        """captures[0] is digitised by admin_user; self_user (D, scope=1) can't delete it."""
        set_logged_user(self.client, users["self_user"])
        r = self.client.delete(
            url_for("individuals.delete_capture", id_capture=captures[0].id_capture)
        )
        assert r.status_code == 403

    def test_not_found_returns_404(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.delete(url_for("individuals.delete_capture", id_capture=-1))
        assert r.status_code == 404

    def test_not_found_returns_structured_error(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.delete(url_for("individuals.delete_capture", id_capture=-1))
        payload = r.get_json()
        assert payload.get("name") == ApiErrorCode.NOT_FOUND
        assert "description" in payload

    def test_returns_204_for_existing_capture(self, users, capture):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.delete(
            url_for("individuals.delete_capture", id_capture=capture.id_capture)
        )
        assert r.status_code == 204

    def test_response_body_is_empty(self, users, capture):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.delete(
            url_for("individuals.delete_capture", id_capture=capture.id_capture)
        )
        assert r.data == b""

    def test_capture_no_longer_exists_after_delete(self, users, capture):
        capture_id = capture.id_capture
        set_logged_user(self.client, users["admin_user"])
        self.client.delete(url_for("individuals.delete_capture", id_capture=capture_id))
        r = self.client.get(url_for("individuals.get_capture_by_id", id_capture=capture_id))
        assert r.status_code == 404

    def test_own_capture_can_be_deleted_by_self_user(self, users, captures):
        """captures[1] is digitised by self_user."""
        set_logged_user(self.client, users["self_user"])
        r = self.client.delete(
            url_for("individuals.delete_capture", id_capture=captures[1].id_capture)
        )
        assert r.status_code == 204
