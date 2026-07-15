import datetime

import pytest
from flask import url_for
from sqlalchemy import func

from geonature.core.gn_synthese.models import Synthese
from geonature.utils.env import db
from pypnusershub.tests.utils import set_logged_user

from gn_module_individuals.utils.errors import IndividualsErrorCode

# ===========================================================================
# GET /individuals/individuals/geometry  (individuals_geometry)
# ===========================================================================


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestIndividualsMap:

    def test_unauthenticated_returns_401(self):
        r = self.client.get(url_for("individuals.individuals_geometry"))
        assert r.status_code == 401

    def test_forbidden_without_rights(self, users):
        set_logged_user(self.client, users["noright_user"])
        r = self.client.get(url_for("individuals.individuals_geometry"))
        assert r.status_code == 403

    def test_returns_200(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.individuals_geometry"))
        assert r.status_code == 200

    def test_response_is_geojson_feature_collection(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.individuals_geometry"))
        data = r.get_json()
        assert data["type"] == "FeatureCollection"
        assert "features" in data
        assert isinstance(data["features"], list)

    def test_features_have_expected_properties(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.individuals_geometry"))
        features = r.get_json()["features"]
        for feature in features:
            assert feature["type"] == "Feature"
            assert "geometry" in feature
            props = feature.get("properties", {})
            assert "id_individual" in props
            assert "individual_name" in props
            assert "last_observation_date" in props
            assert "last_observation_observers_name" in props
            assert "taxon_vern_nom" in props

    def test_features_have_geometry(self, users):
        """All returned individuals have a geometry (filtered server-side)."""
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.individuals_geometry"))
        features = r.get_json()["features"]
        for feature in features:
            assert feature["geometry"] is not None

    def test_individual_without_synthese_data_is_excluded(self, users, individual):
        """An individual with no linked synthese row has no known position and
        must not appear on the map."""
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.individuals_geometry"))
        ids = [f["properties"]["id_individual"] for f in r.get_json()["features"]]
        assert individual.id_individual not in ids

    def test_individual_with_synthese_data_is_included(self, users, source, individual):
        """An individual with a linked synthese row appears with its geometry."""
        geom = func.ST_SetSRID(func.ST_MakePoint(6.0, 45.0), 4326)
        with db.session.begin_nested():
            db.session.add(
                Synthese(
                    id_source=source.id_source,
                    id_individual=individual.id_individual,
                    nom_cite="Test",
                    the_geom_4326=geom,
                    the_geom_point=geom,
                    date_min=datetime.datetime(2026, 7, 1),
                    date_max=datetime.datetime(2026, 7, 1),
                    observers="Observateur Test",
                )
            )

        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.individuals_geometry"))
        feature = next(
            f
            for f in r.get_json()["features"]
            if f["properties"]["id_individual"] == individual.id_individual
        )
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
        "cruved",
        "id_individual",
        "individual_name",
        "id_digitiser",
        "active",
        "taxon_cd_nom",
        "taxon_vern_nom",
        "taxon_lb_nom",
        "meta_create_date",
        "meta_update_date",
        "id_nomenclature_sex",
        "nomenclature_sex_name",
        "digitiser_name",
        "comment",
        "additional_data",
        "last_observation_date",
        "last_observation_observers_name",
        "deployed_devices",
        "deployed_markings",
    }

    def test_item_contains_expected_fields(self, users, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_individuals"))
        items = r.get_json()["items"]
        assert len(items) > 0, "At least one individual expected"
        item = next(i for i in items if i["id_individual"] == individual.id_individual)
        missing = self.EXPECTED_FIELDS - item.keys()
        assert not missing, f"Missing fields in item: {missing}"
        # No relationship object is exposed in the list, only computed fields.
        assert "taxref" not in item
        assert "nomenclature_sex" not in item
        assert "deployments" not in item
        # cd_nom/nom_vern are renamed taxon_cd_nom/taxon_vern_nom, not duplicated.
        assert "cd_nom" not in item
        assert "nom_vern" not in item

    def test_deployed_devices_and_markings_are_empty_dict_without_deployment(
        self, users, individual
    ):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_individuals"))
        item = next(
            i for i in r.get_json()["items"] if i["id_individual"] == individual.id_individual
        )
        assert item["deployed_devices"] == {}
        assert item["deployed_markings"] == {}

    def test_last_observation_is_none_without_synthese_data(self, users, individual):
        """last_observation_date/observers_name are null when the individual has
        no linked synthese row."""
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_individuals"))
        item = next(
            i for i in r.get_json()["items"] if i["id_individual"] == individual.id_individual
        )
        assert item["last_observation_date"] is None
        assert item["last_observation_observers_name"] is None

    def test_last_observation_reflects_synthese_data(self, users, source, individual):
        """last_observation_date/observers_name are built from the most recent
        gn_synthese.synthese row linked to the individual (models/individuals.py)."""
        geom = func.ST_SetSRID(func.ST_MakePoint(6.0, 45.0), 4326)
        with db.session.begin_nested():
            db.session.add(
                Synthese(
                    id_source=source.id_source,
                    id_individual=individual.id_individual,
                    nom_cite="Test",
                    the_geom_4326=geom,
                    the_geom_point=geom,
                    date_min=datetime.datetime(2026, 7, 1),
                    date_max=datetime.datetime(2026, 7, 1),
                    observers="Observateur Test",
                )
            )

        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_individuals"))
        item = next(
            i for i in r.get_json()["items"] if i["id_individual"] == individual.id_individual
        )
        assert item["last_observation_date"] == "01-07-2026"
        assert item["last_observation_observers_name"] == "Observateur Test"

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
        assert all(item["taxon_cd_nom"] == individual.cd_nom for item in items)

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

    def test_individual_with_device_deployment_has_no_marking(
        self, users, device_with_deployment, individual
    ):
        """A deployment with a tracking device is not a physical marking."""
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_individuals"))
        items = r.get_json()["items"]
        item = next(i for i in items if i["id_individual"] == individual.id_individual)
        assert item["deployed_markings"] == {}
        # device_with_deployment uses a device without id_nomenclature_device_type set
        assert item["deployed_devices"] == {
            "device_1": {"location_name": "Encolure", "name": None}
        }

    def test_filter_bbox_restricts_results(self, users, individuals):
        """Individuals without any synthese observation have no geometry, so any
        bbox filter excludes them."""
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

    def test_default_sort_is_last_obs_date_desc(self, users):
        """Without explicit prop/dir, the list is sorted by last observation
        date, most recent first."""
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_individuals"))
        assert r.status_code == 200
        payload = r.get_json()
        assert payload["prop"] == "last_obs_date"
        assert payload["dir"] == "desc"

    def test_prop_and_dir_are_echoed_without_pagination(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(
            url_for("individuals.list_individuals", prop="individual_name", dir="asc")
        )
        payload = r.get_json()
        assert payload["prop"] == "individual_name"
        assert payload["dir"] == "asc"

    def test_prop_and_dir_are_echoed_with_pagination(self, users, individuals):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(
            url_for(
                "individuals.list_individuals",
                prop="individual_name",
                dir="asc",
                page=1,
                per_page=2,
            )
        )
        payload = r.get_json()
        assert payload["prop"] == "individual_name"
        assert payload["dir"] == "asc"

    def test_item_has_cruved(self, users, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_individuals"))
        item = next(
            i for i in r.get_json()["items"] if i["id_individual"] == individual.id_individual
        )
        assert set(item["cruved"].keys()) == {"C", "R", "U", "V", "E", "D"}


# ===========================================================================
# GET /individuals/individuals/<id>  (individual)
# ===========================================================================


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestGetIndividual:

    def test_unauthenticated_returns_401(self, individual):
        r = self.client.get(
            url_for("individuals.individual", id_individual=individual.id_individual)
        )
        assert r.status_code == 401

    def test_forbidden_without_rights(self, users, individual):
        set_logged_user(self.client, users["noright_user"])
        r = self.client.get(
            url_for("individuals.individual", id_individual=individual.id_individual)
        )
        assert r.status_code == 403

    def test_not_found_returns_404(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.individual", id_individual=-1))
        assert r.status_code == 404

    def test_not_found_returns_structured_error(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.individual", id_individual=-1))
        payload = r.get_json()
        assert payload.get("name") == IndividualsErrorCode.INDIVIDUAL_NOT_FOUND
        assert "description" in payload

    def test_out_of_scope_individual_returns_404(self, users, individuals):
        """individuals[0] is digitised by admin_user; self_user (scope=1) can't see it."""
        set_logged_user(self.client, users["self_user"])
        r = self.client.get(
            url_for("individuals.individual", id_individual=individuals[0].id_individual)
        )
        assert r.status_code == 404

    def test_returns_200_for_existing_individual(self, users, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(
            url_for("individuals.individual", id_individual=individual.id_individual)
        )
        assert r.status_code == 200

    EXPECTED_FIELDS = {
        "cruved",
        "id_individual",
        "uuid_individual",
        "individual_name",
        "active",
        "cd_nom",
        "nom_vern",
        "lb_nom",
        "meta_create_date",
        "meta_update_date",
        "id_nomenclature_sex",
        "nomenclature_sex",
        "digitiser",
        "comment",
        "additional_data",
        "deployments",
    }

    def test_payload_contains_expected_fields(self, users, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(
            url_for("individuals.individual", id_individual=individual.id_individual)
        )
        payload = r.get_json()
        missing = self.EXPECTED_FIELDS - payload.keys()
        assert not missing, f"Missing fields in payload: {missing}"
        # Only the nested digitiser object is exposed, not the raw FK, and none
        # of the list-specific computed fields (those belong to IndividualsListSchema).
        assert "id_digitiser" not in payload
        assert "taxon_cd_nom" not in payload
        assert "digitiser_name" not in payload
        assert "deployed_devices" not in payload
        assert "deployed_markings" not in payload

    def test_payload_id_matches(self, users, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(
            url_for("individuals.individual", id_individual=individual.id_individual)
        )
        assert r.get_json()["id_individual"] == individual.id_individual

    def test_digitiser_is_nested_object(self, users, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(
            url_for("individuals.individual", id_individual=individual.id_individual)
        )
        digitiser = r.get_json()["digitiser"]
        assert isinstance(digitiser, dict)
        assert digitiser["id_role"] == individual.id_digitiser

    def test_deployments_is_empty_list_without_deployment(self, users, individual):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(
            url_for("individuals.individual", id_individual=individual.id_individual)
        )
        assert r.get_json()["deployments"] == []

    def test_deployments_excludes_removed_deployment(
        self, users, device_with_deployment, individual
    ):
        """Only active deployments (removal_date NULL) appear in deployments."""
        individual.deployments[0].removal_date = datetime.datetime(2024, 6, 1)
        db.session.flush()
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(
            url_for("individuals.individual", id_individual=individual.id_individual)
        )
        assert r.get_json()["deployments"] == []

    def test_deployments_shape_for_active_device_deployment(
        self, users, device_with_deployment, individual
    ):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(
            url_for("individuals.individual", id_individual=individual.id_individual)
        )
        deployments = r.get_json()["deployments"]
        assert len(deployments) == 1
        dep = deployments[0]
        assert dep["id_tracking_device"] == device_with_deployment.id_tracking_device
        assert dep["provider_device_id"] == device_with_deployment.provider_device_id
        assert dep["device_type_name"] is None  # device fixture has no nomenclature type set
        assert dep["install_date"] == "01-01-2024"
        assert dep["marking_code"] is None
        assert dep["deployment_location_name"] == "Encolure"
        assert dep["deployment_type_name"] == "Dispositif de suivi"


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

    def test_rank_is_independent_of_per_page_but_page_is_not(self, users, individuals):
        """rank is the individual's absolute position in the sorted/filtered list
        (independent of per_page); page is derived from rank using per_page."""
        set_logged_user(self.client, users["admin_user"])
        cd_nom = individuals[0].cd_nom
        target = individuals[0]

        responses = {}
        for per_page in (1, 2, 3):
            r = self.client.get(
                url_for(
                    "individuals.individual_page",
                    id_individual=target.id_individual,
                    prop="individual_name",
                    dir="asc",
                    taxon=cd_nom,
                    per_page=per_page,
                )
            )
            responses[per_page] = r.get_json()

        ranks = {payload["rank"] for payload in responses.values()}
        assert len(ranks) == 1, "rank must not depend on per_page"

        rank = next(iter(ranks))
        for per_page, payload in responses.items():
            assert payload["page"] == ((rank - 1) // per_page) + 1

    def test_rank_reflects_sort_prop_asc(self, users, individuals):
        """individuals: [0]='Individu Actif Admin', [1]='Individu Inactif Admin',
        [2]='Individu Actif Self'. Sorted asc by individual_name: [0],[2],[1] -> ranks 1,2,3.
        Scoped via taxon= to just these 3 (shared DB has other individuals too)."""
        set_logged_user(self.client, users["admin_user"])
        cd_nom = individuals[0].cd_nom
        expected_ranks = {
            individuals[0].id_individual: 1,
            individuals[2].id_individual: 2,
            individuals[1].id_individual: 3,
        }
        for ind_id, expected_rank in expected_ranks.items():
            r = self.client.get(
                url_for(
                    "individuals.individual_page",
                    id_individual=ind_id,
                    prop="individual_name",
                    dir="asc",
                    taxon=cd_nom,
                )
            )
            assert r.get_json()["rank"] == expected_rank

    def test_rank_reflects_sort_prop_desc(self, users, individuals):
        """dir=desc must flip the order entirely, not just the asc order."""
        set_logged_user(self.client, users["admin_user"])
        cd_nom = individuals[0].cd_nom
        expected_ranks = {
            individuals[1].id_individual: 1,
            individuals[2].id_individual: 2,
            individuals[0].id_individual: 3,
        }
        for ind_id, expected_rank in expected_ranks.items():
            r = self.client.get(
                url_for(
                    "individuals.individual_page",
                    id_individual=ind_id,
                    prop="individual_name",
                    dir="desc",
                    taxon=cd_nom,
                )
            )
            assert r.get_json()["rank"] == expected_rank
