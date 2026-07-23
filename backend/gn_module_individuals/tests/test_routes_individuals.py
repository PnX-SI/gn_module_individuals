import pytest
from flask import url_for

from pypnusershub.tests.utils import set_logged_user

# ===========================================================================
# GET /individuals/individuals/map  (individuals_map)
# ===========================================================================


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestIndividualsMap:

    def test_unauthenticated_returns_401(self):
        r = self.client.get(url_for("individuals.individuals_map"))
        assert r.status_code == 401

    def test_forbidden_without_rights(self, users):
        set_logged_user(self.client, users["noright_user"])
        r = self.client.get(url_for("individuals.individuals_map"))
        assert r.status_code == 403

    def test_returns_200(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.individuals_map"))
        assert r.status_code == 200

    def test_response_is_geojson_feature_collection(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.individuals_map"))
        data = r.get_json()
        assert data["type"] == "FeatureCollection"
        assert "features" in data
        assert isinstance(data["features"], list)

    def test_features_have_expected_properties(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.individuals_map"))
        features = r.get_json()["features"]
        for feature in features:
            assert feature["type"] == "Feature"
            assert "geometry" in feature
            props = feature.get("properties", {})
            assert "id_individual" in props
            assert "individual_name" in props
            assert "last_observation" in props
            assert "nom_vern" in props

    def test_features_have_geometry(self, users):
        """All returned individuals have a geometry (filtered server-side)."""
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.individuals_map"))
        features = r.get_json()["features"]
        for feature in features:
            assert feature["geometry"] is not None


# ===========================================================================
# GET /individuals/individuals  (list_individuals)
# ===========================================================================


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestListIndividuals:

    def test_unauthenticated_returns_401(self):
        r = self.client.get(url_for("individuals.list_individuals"))
        assert r.status_code == 401

    def test_forbidden_without_rights(self, users):
        set_logged_user(self.client, users["noright_user"])
        r = self.client.get(url_for("individuals.list_individuals"))
        assert r.status_code == 403

    def test_returns_200_with_items_key(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_individuals"))
        assert r.status_code == 200
        payload = r.get_json()
        assert "items" in payload
        assert isinstance(payload["items"], list)

    def test_no_pagination_key_without_page_params(self, users):
        """Without page/per_page, the response does not contain pagination keys."""
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_individuals"))
        payload = r.get_json()
        assert "total" not in payload
        assert "pages" not in payload

    EXPECTED_FIELDS = {
        "id_individual",
        "individual_name",
        "cd_nom",
        "id_nomenclature_sex",
        "active",
        "taxref",
        "nomenclature_sex",
        "digitiser_name",
        "last_observation",
        "deployments",
        "meta_create_date",
    }

    def test_item_contains_expected_fields(self, users, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_individuals"))
        items = r.get_json()["items"]
        assert len(items) > 0, "At least one individual expected"
        item = next(i for i in items if i["id_individual"] == individual.id_individual)
        missing = self.EXPECTED_FIELDS - item.keys()
        assert not missing, f"Missing fields in item: {missing}"

    def test_taxref_is_object_when_present(self, users, individual):
        """taxref is a TaxrefSchema object (valid cd_nom) or null."""
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_individuals"))
        items = r.get_json()["items"]
        item = next(i for i in items if i["id_individual"] == individual.id_individual)
        # individual fixture uses a valid cd_nom → taxref must be an object
        assert item["taxref"] is not None
        assert "cd_nom" in item["taxref"]

    def test_deployments_is_list(self, users, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_individuals"))
        item = next(
            i for i in r.get_json()["items"] if i["id_individual"] == individual.id_individual
        )
        assert isinstance(item["deployments"], list)

    def test_last_observation_has_expected_shape(self, users, individual):
        """last_observation is a temporary mock (see models/individuals.py): always a dict
        with date/observateurs keys, since the real occtax join is not wired up yet."""
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_individuals"))
        item = next(
            i for i in r.get_json()["items"] if i["id_individual"] == individual.id_individual
        )
        last_observation = item["last_observation"]
        assert isinstance(last_observation, dict)
        assert "date" in last_observation
        assert "observateurs" in last_observation

    def test_with_pagination_returns_paginated_envelope(self, users, individuals):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_individuals", page=1, per_page=2))
        assert r.status_code == 200
        payload = r.get_json()
        for key in ("items", "page", "per_page", "total", "pages", "has_next", "has_prev"):
            assert key in payload, f"Missing key in paginated response: {key}"
        assert isinstance(payload["items"], list)

    def test_pagination_limits_results(self, users, individuals):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_individuals", page=1, per_page=1))
        payload = r.get_json()
        assert len(payload["items"]) == 1
        assert payload["per_page"] == 1
        assert payload["page"] == 1

    def test_pagination_total_reflects_all_individuals(self, users, individuals):
        set_logged_user(self.client, users["admin_user"])
        r_all = self.client.get(url_for("individuals.list_individuals"))
        total_unpaged = len(r_all.get_json()["items"])

        r_paged = self.client.get(url_for("individuals.list_individuals", page=1, per_page=1))
        assert r_paged.get_json()["total"] == total_unpaged

    def test_filter_by_taxon_no_match(self, users, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_individuals", taxon=-999))
        assert r.status_code == 200
        assert r.get_json()["items"] == []

    def test_filter_by_taxon_matching(self, users, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_individuals", taxon=individual.cd_nom))
        assert r.status_code == 200
        items = r.get_json()["items"]
        assert len(items) >= 1
        assert all(item["cd_nom"] == individual.cd_nom for item in items)

    def test_filter_active_true_excludes_inactive(self, users, individuals):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_individuals", active="true"))
        assert r.status_code == 200
        items = r.get_json()["items"]
        assert all(item["active"] is True for item in items)

    def test_filter_active_false_returns_only_inactive(self, users, individuals):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_individuals", active="false"))
        assert r.status_code == 200
        items = r.get_json()["items"]
        # The fixture creates 1 inactive individual
        assert len(items) >= 1
        assert all(item["active"] is False for item in items)

    def test_scope_restricts_to_own_data(self, users, individuals):
        """self_user (scope=1) only sees individuals they digitised."""
        set_logged_user(self.client, users["self_user"])
        r = self.client.get(url_for("individuals.list_individuals"))
        assert r.status_code == 200
        items = r.get_json()["items"]
        assert len(items) >= 1
        assert all(item["id_digitiser"] == users["self_user"].id_role for item in items)

    def test_individual_with_deployment_shows_deployment(
        self, users, device_with_deployment, individual
    ):
        """An individual with a deployment correctly exposes its deployments in the list."""
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_individuals"))
        items = r.get_json()["items"]
        item = next(i for i in items if i["id_individual"] == individual.id_individual)
        assert isinstance(item["deployments"], list)
        assert len(item["deployments"]) >= 1
        dep = item["deployments"][0]
        assert "install_date" in dep
        assert "marking_code" in dep
        assert "nomenclature_deployment_type" in dep
        assert "nomenclature_deployment_location" in dep

    def test_filter_bbox_restricts_results(self, users, individuals):
        """A bbox far from the temporary mock positions excludes every individual."""
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_individuals", bbox="-10,-10,-9,-9"))
        assert r.status_code == 200
        assert r.get_json()["items"] == []

    def test_filter_bbox_invalid_returns_400(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_individuals", bbox="not-a-bbox"))
        assert r.status_code == 400

    def test_sort_by_individual_name_desc(self, users, individuals):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(
            url_for("individuals.list_individuals", prop="individual_name", dir="desc")
        )
        assert r.status_code == 200
        names = [item["individual_name"] for item in r.get_json()["items"]]
        assert names == sorted(names, reverse=True)

    def test_sort_invalid_dir_returns_400(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_individuals", dir="sideways"))
        assert r.status_code == 400


# ===========================================================================
# GET /individuals/individuals/<id>/page  (individual_page)
# ===========================================================================


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestIndividualPage:

    def test_unauthenticated_returns_401(self, individual):
        r = self.client.get(
            url_for("individuals.individual_page", id_individual=individual.id_individual)
        )
        assert r.status_code == 401

    def test_forbidden_without_rights(self, users, individual):
        set_logged_user(self.client, users["noright_user"])
        r = self.client.get(
            url_for("individuals.individual_page", id_individual=individual.id_individual)
        )
        assert r.status_code == 403

    def test_unknown_individual_returns_404(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.individual_page", id_individual=-1))
        assert r.status_code == 404

    def test_out_of_scope_individual_returns_404(self, users, individuals):
        """individuals[0] is digitised by admin_user; self_user (scope=1) can't see it."""
        set_logged_user(self.client, users["self_user"])
        r = self.client.get(
            url_for("individuals.individual_page", id_individual=individuals[0].id_individual)
        )
        assert r.status_code == 404

    def test_page_is_consistent_with_list(self, users, individuals):
        set_logged_user(self.client, users["admin_user"])
        per_page = 1
        target = individuals[-1]

        r = self.client.get(
            url_for(
                "individuals.individual_page",
                id_individual=target.id_individual,
                per_page=per_page,
            )
        )
        assert r.status_code == 200
        page = r.get_json()["page"]

        r_list = self.client.get(
            url_for("individuals.list_individuals", page=page, per_page=per_page)
        )
        ids_on_page = [item["id_individual"] for item in r_list.get_json()["items"]]
        assert target.id_individual in ids_on_page
