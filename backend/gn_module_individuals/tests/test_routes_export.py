import csv
import io

import pytest
from flask import url_for

from pypnusershub.tests.utils import set_logged_user

# ===========================================================================
# POST /individuals/export/<export_format>  (export_individuals)
# ===========================================================================


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestExportIndividuals:
    def test_unauthenticated_returns_401(self):
        r = self.client.post(url_for("individuals.export_individuals", export_format="csv"))
        assert r.status_code == 401

    def test_forbidden_without_rights(self, users):
        set_logged_user(self.client, users["noright_user"])
        r = self.client.post(url_for("individuals.export_individuals", export_format="csv"))
        assert r.status_code == 403

    def test_unsupported_format_returns_400(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(url_for("individuals.export_individuals", export_format="shapefile"))
        assert r.status_code == 400

    def test_csv_returns_attachment(self, users, individuals):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(url_for("individuals.export_individuals", export_format="csv"))
        assert r.status_code == 200
        assert "attachment" in r.headers["Content-Disposition"]

    def test_csv_contains_expected_rows(self, users, individuals):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(url_for("individuals.export_individuals", export_format="csv"))
        rows = list(csv.DictReader(io.StringIO(r.get_data(as_text=True)), delimiter=";"))
        names = {row["individual_name"] for row in rows}
        assert {i.individual_name for i in individuals} <= names

    def test_csv_respects_active_filter(self, users, individuals):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.export_individuals", export_format="csv", active="false")
        )
        rows = list(csv.DictReader(io.StringIO(r.get_data(as_text=True)), delimiter=";"))
        names = {row["individual_name"] for row in rows}
        assert "Individu Inactif Admin" in names
        assert "Individu Actif Admin" not in names

    def test_csv_respects_scope(self, users, individuals):
        # self_user has E/R with scope=1 (own data only): only the individual
        # digitised by self_user must be exported.
        set_logged_user(self.client, users["self_user"])
        r = self.client.post(url_for("individuals.export_individuals", export_format="csv"))
        rows = list(csv.DictReader(io.StringIO(r.get_data(as_text=True)), delimiter=";"))
        names = {row["individual_name"] for row in rows}
        assert "Individu Actif Self" in names
        assert "Individu Actif Admin" not in names

    def test_geojson_returns_feature_collection(self, users, individuals):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(url_for("individuals.export_individuals", export_format="geojson"))
        assert r.status_code == 200
        payload = r.get_json()
        assert payload["type"] == "FeatureCollection"
        ids = {feature["properties"]["id_individual"] for feature in payload["features"]}
        assert {i.id_individual for i in individuals} <= ids

    def test_gpkg_returns_attachment(self, users, individuals):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(url_for("individuals.export_individuals", export_format="gpkg"))
        assert r.status_code == 200
        assert "attachment" in r.headers["Content-Disposition"]
        assert r.data  # non-empty binary content


# ===========================================================================
# POST /devices/export/<export_format>  (export_devices)
# ===========================================================================


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestExportDevices:
    def test_unauthenticated_returns_401(self):
        r = self.client.post(url_for("individuals.export_devices", export_format="csv"))
        assert r.status_code == 401

    def test_forbidden_without_rights(self, users):
        set_logged_user(self.client, users["noright_user"])
        r = self.client.post(url_for("individuals.export_devices", export_format="csv"))
        assert r.status_code == 403

    def test_unsupported_format_returns_400(self, users):
        # geojson/gpkg are not in DevicesSchema.EXPORT_FORMAT (devices have no geometry).
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(url_for("individuals.export_devices", export_format="geojson"))
        assert r.status_code == 400

    def test_csv_returns_attachment(self, users, devices):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(url_for("individuals.export_devices", export_format="csv"))
        assert r.status_code == 200
        assert "attachment" in r.headers["Content-Disposition"]

    def test_csv_contains_expected_rows(self, users, devices):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(url_for("individuals.export_devices", export_format="csv"))
        rows = list(csv.DictReader(io.StringIO(r.get_data(as_text=True)), delimiter=";"))
        provider_ids = {row["provider_device_id"] for row in rows}
        assert {d.provider_device_id for d in devices} <= provider_ids

    def test_csv_respects_provider_name_filter(self, users, devices):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.post(
            url_for("individuals.export_devices", export_format="csv", provider_name="Lotek")
        )
        rows = list(csv.DictReader(io.StringIO(r.get_data(as_text=True)), delimiter=";"))
        provider_names = {row["provider_name"] for row in rows}
        assert provider_names <= {"Lotek"}
        assert "Balise 57" in {row["provider_device_id"] for row in rows}
