import pytest
from flask import url_for
from pypnusershub.tests.utils import logged_user


# ===========================================================================
# GET /devices  (list_devices)
# ===========================================================================


class TestListDevices:

    # --- format de réponse ---------------------------------------------------

    def test_without_pagination_returns_list(self, client, users):
        with logged_user(client, users["admin_user"]):
            response = client.get(url_for("individuals.list_devices"))
        assert response.status_code == 200
        assert isinstance(response.get_json(), list)

    def test_with_pagination_returns_paginated_object(self, client, users, devices):
        with logged_user(client, users["admin_user"]):
            response = client.get(
                url_for("individuals.list_devices", page=1, per_page=2)
            )
        assert response.status_code == 200
        payload = response.get_json()
        for key in ("items", "page", "per_page", "total", "pages", "has_next", "has_prev"):
            assert key in payload, f"Clé manquante dans la réponse paginée : {key}"
        assert isinstance(payload["items"], list)

    def test_pagination_page_and_per_page(self, client, users, devices):
        with logged_user(client, users["admin_user"]):
            r = client.get(url_for("individuals.list_devices", page=1, per_page=1))
        payload = r.get_json()
        assert len(payload["items"]) == 1
        assert payload["per_page"] == 1
        assert payload["page"] == 1

    # --- champs présents dans chaque item ------------------------------------

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

    def test_item_contains_expected_fields(self, client, users, device):
        with logged_user(client, users["admin_user"]):
            r = client.get(url_for("individuals.list_devices", page=1, per_page=1))
        item = r.get_json()["items"][0]
        missing = self.EXPECTED_FIELDS - item.keys()
        assert not missing, f"Champs manquants dans l'item : {missing}"


    def test_filter_by_provider_name_no_match(self, client, users, devices):
        with logged_user(client, users["admin_user"]):
            r = client.get(
                url_for("individuals.list_devices", providerName="__no_match_xyz__")
            )
        assert r.get_json() == []

 
    def test_forbidden_without_rights(self, client, users):
        with logged_user(client, users["noright_user"]):
            r = client.get(url_for("individuals.list_devices"))
        assert r.status_code == 403

    def test_unauthenticated_returns_401(self, client):
        r = client.get(url_for("individuals.list_devices"))
        assert r.status_code == 401


# ===========================================================================
# GET /devices/<id>  (device)
# ===========================================================================


class TestGetDevice:

    # --- cas nominal ---------------------------------------------------------

    def test_returns_200_for_existing_device(self, client, users, device):
        with logged_user(client, users["admin_user"]):
            r = client.get(
                url_for("individuals.device", id_tracking_device=device.id_tracking_device)
            )
        assert r.status_code == 200

    def test_payload_id_matches(self, client, users, device):
        with logged_user(client, users["admin_user"]):
            r = client.get(
                url_for("individuals.device", id_tracking_device=device.id_tracking_device)
            )
        assert r.get_json()["id_tracking_device"] == device.id_tracking_device

    # --- cas d'erreur --------------------------------------------------------

    def test_not_found_returns_404(self, client, users):
        with logged_user(client, users["admin_user"]):
            r = client.get(url_for("individuals.device", id_tracking_device=-1))
        assert r.status_code == 404

    def test_forbidden_without_rights(self, client, users, device):
        with logged_user(client, users["noright_user"]):
            r = client.get(
                url_for("individuals.device", id_tracking_device=device.id_tracking_device)
            )
        assert r.status_code == 403

    def test_unauthenticated_returns_401(self, client, device):
        r = client.get(
            url_for("individuals.device", id_tracking_device=device.id_tracking_device)
        )
        assert r.status_code == 401