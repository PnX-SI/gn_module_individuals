import datetime

import pytest
from flask import url_for
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy import select

from apptax.taxonomie.models import Taxref
from geonature.tests.fixtures import create_synthese
from geonature.utils.env import db
from pypnusershub.tests.utils import set_logged_user


@pytest.fixture
def observations(users, datasets, source, individuals):
    """4 synthese observations readable by admin_user: 2 for individuals[0],
    1 for individuals[2] (in another dataset), 1 without individual."""
    taxon = db.session.scalar(select(Taxref).where(Taxref.cd_nom == individuals[0].cd_nom))
    geom = from_shape(Point(6.9, 45.4), srid=4326)
    obs = {}
    with db.session.begin_nested():
        for key, individual, dataset, date in [
            ("ind0_old", individuals[0], "own_dataset", datetime.datetime(2024, 1, 10)),
            ("ind0_recent", individuals[0], "own_dataset", datetime.datetime(2024, 3, 5)),
            ("ind2", individuals[2], "belong_af_1", datetime.datetime(2024, 2, 1)),
            ("no_individual", None, "own_dataset", datetime.datetime(2024, 2, 15)),
        ]:
            obs[key] = create_synthese(
                geom,
                taxon,
                users["admin_user"],
                datasets[dataset],
                source,
                id_individual=individual.id_individual if individual else None,
                date_min=date,
                date_max=date,
                comment_description=key,
            )
            db.session.add(obs[key])
    return obs


def _ids(items, observations):
    """id_synthese of the returned items that belong to the observations fixture
    (the test database may contain other synthese data), in the returned order."""
    fixture_ids = {o.id_synthese for o in observations.values()}
    return [item["id_synthese"] for item in items if item["id_synthese"] in fixture_ids]


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestListObservations:
    def _get(self, **params):
        r = self.client.get(url_for("individuals.list_observations", **params))
        assert r.status_code == 200, r.get_json()
        return r.get_json()

    def test_unauthenticated_returns_401(self):
        r = self.client.get(url_for("individuals.list_observations"))
        assert r.status_code == 401

    def test_no_synthese_permission_returns_403(self, users):
        set_logged_user(self.client, users["noright_user"])
        r = self.client.get(url_for("individuals.list_observations"))
        assert r.status_code == 403

    def test_blurring_permission_returns_403(self, users):
        set_logged_user(self.client, users["user_with_blurring"])
        r = self.client.get(url_for("individuals.list_observations"))
        assert r.status_code == 403

    def test_only_observations_with_individual(self, users, observations):
        set_logged_user(self.client, users["admin_user"])
        items = self._get()["items"]
        assert all(item["id_individual"] is not None for item in items)
        assert set(_ids(items, observations)) == {
            observations["ind0_old"].id_synthese,
            observations["ind0_recent"].id_synthese,
            observations["ind2"].id_synthese,
        }

    def test_individual_name_and_columns(self, app, users, observations, individuals):
        set_logged_user(self.client, users["admin_user"])
        items = self._get(id_individual=individuals[2].id_individual)["items"]
        assert len(items) == 1
        item = items[0]
        assert item["id_synthese"] == observations["ind2"].id_synthese
        assert item["id_individual"] == individuals[2].id_individual
        assert item["individual_name"] == individuals[2].individual_name
        list_columns = app.config["INDIVIDUALS"]["OBSERVATIONS"]["LIST_COLUMNS"]
        assert set(list_columns) <= item.keys()

    def test_filter_several_individuals(self, users, observations, individuals):
        set_logged_user(self.client, users["admin_user"])
        items = self._get(
            id_individual=[individuals[0].id_individual, individuals[2].id_individual]
        )["items"]
        assert len(items) == 3

    def test_filter_individual_without_observation(self, users, observations, individuals):
        set_logged_user(self.client, users["admin_user"])
        assert self._get(id_individual=individuals[1].id_individual)["items"] == []

    def test_filter_individual_name(self, users, observations, individuals):
        set_logged_user(self.client, users["admin_user"])
        # Partial and case insensitive match
        name_part = individuals[2].individual_name[3:-2].upper()
        items = self._get(individual_name=name_part)["items"]
        assert _ids(items, observations) == [observations["ind2"].id_synthese]

    def test_filter_dataset(self, users, datasets, observations):
        set_logged_user(self.client, users["admin_user"])
        items = self._get(id_dataset=datasets["belong_af_1"].id_dataset)["items"]
        assert _ids(items, observations) == [observations["ind2"].id_synthese]

    def test_filter_dates(self, users, observations):
        set_logged_user(self.client, users["admin_user"])
        items = self._get(date_min="2024-01-15", date_max="2024-02-28")["items"]
        assert _ids(items, observations) == [observations["ind2"].id_synthese]

    def test_bad_date_returns_400(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_observations", date_min="01/02/2024"))
        assert r.status_code == 400

    def test_default_sort_date_desc(self, users, observations):
        set_logged_user(self.client, users["admin_user"])
        payload = self._get()
        assert (payload["prop"], payload["dir"]) == ("date_min", "desc")
        assert _ids(payload["items"], observations) == [
            observations["ind0_recent"].id_synthese,
            observations["ind2"].id_synthese,
            observations["ind0_old"].id_synthese,
        ]

    def test_sort_date_asc(self, users, observations):
        set_logged_user(self.client, users["admin_user"])
        items = self._get(prop="date_min", dir="asc")["items"]
        assert _ids(items, observations) == [
            observations["ind0_old"].id_synthese,
            observations["ind2"].id_synthese,
            observations["ind0_recent"].id_synthese,
        ]

    def test_sort_individual_name(self, users, observations, individuals):
        set_logged_user(self.client, users["admin_user"])
        items = self._get(
            id_individual=[individuals[0].id_individual, individuals[2].id_individual],
            prop="individual_name",
            dir="asc",
        )["items"]
        names = [item["individual_name"] for item in items]
        assert names == sorted(names)

    def test_bad_sort_dir_returns_400(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_observations", dir="up"))
        assert r.status_code == 400

    def test_pagination(self, users, observations, individuals):
        set_logged_user(self.client, users["admin_user"])
        params = {"id_individual": individuals[0].id_individual, "per_page": 1}
        page_1 = self._get(page=1, **params)
        page_2 = self._get(page=2, **params)
        assert page_1["total"] == 2
        assert page_1["pages"] == 2
        assert page_1["has_next"] and not page_2["has_next"]
        assert [page_1["items"][0]["id_synthese"], page_2["items"][0]["id_synthese"]] == [
            observations["ind0_recent"].id_synthese,
            observations["ind0_old"].id_synthese,
        ]


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestObservationsGeometry:
    def _features(self, **params):
        r = self.client.get(url_for("individuals.observations_geometry", **params))
        assert r.status_code == 200, r.get_json()
        payload = r.get_json()
        assert payload["type"] == "FeatureCollection"
        return payload["features"]

    def test_unauthenticated_returns_401(self):
        r = self.client.get(url_for("individuals.observations_geometry"))
        assert r.status_code == 401

    def test_blurring_permission_returns_403(self, users):
        set_logged_user(self.client, users["user_with_blurring"])
        r = self.client.get(url_for("individuals.observations_geometry"))
        assert r.status_code == 403

    def test_features(self, users, observations, individuals):
        set_logged_user(self.client, users["admin_user"])
        features = self._features(id_individual=individuals[2].id_individual)
        assert len(features) == 1
        feature = features[0]
        assert feature["id"] == observations["ind2"].id_synthese
        assert feature["geometry"] == {"type": "Point", "coordinates": [6.9, 45.4]}
        assert feature["properties"]["individual_name"] == individuals[2].individual_name
        assert feature["properties"].keys() == {
            "id_synthese",
            "nom_vern_or_lb_nom",
            "date_min",
            "observers",
            "id_individual",
            "individual_name",
        }

    def test_only_observations_with_individual(self, users, observations):
        set_logged_user(self.client, users["admin_user"])
        features = self._features()
        assert all(f["properties"]["id_individual"] is not None for f in features)
        assert observations["no_individual"].id_synthese not in {f["id"] for f in features}

    def test_same_filters_as_list(self, users, observations):
        set_logged_user(self.client, users["admin_user"])
        features = self._features(date_min="2024-01-15", date_max="2024-02-28")
        assert _ids([f["properties"] for f in features], observations) == [
            observations["ind2"].id_synthese
        ]
