import pytest
from flask import url_for

from pypnusershub.tests.utils import set_logged_user


@pytest.mark.usefixtures("client_class", "temporary_transaction")
class TestListObservations:
    """`/observations` is currently a stub returning a hardcoded FeatureCollection
    (no database access, no CRUVED scope check yet)."""

    def test_unauthenticated_returns_401(self):
        r = self.client.get(url_for("individuals.list_observations"))
        assert r.status_code == 401

    def test_authenticated_returns_200(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_observations"))
        assert r.status_code == 200

    def test_response_shape(self, users):
        set_logged_user(self.client, users["admin_user"])
        r = self.client.get(url_for("individuals.list_observations"))
        payload = r.get_json()
        assert payload.keys() == {"total", "page", "items"}
        assert payload["items"]["type"] == "FeatureCollection"
        assert payload["total"] == len(payload["items"]["features"])
