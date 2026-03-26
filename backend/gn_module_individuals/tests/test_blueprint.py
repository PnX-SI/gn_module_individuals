from flask import url_for
from pypnusershub.tests.utils import logged_user


def test_list_devices_returns_paginated_list(client, users):
    with logged_user(client, users["admin_user"]):
        response = client.get(url_for("individuals.list_devices"))

    payload = response.get_json()
    assert response.status_code == 200
    assert isinstance(payload, dict)
    assert payload.get("items") is not None
    assert isinstance(payload.get("items"), list)
    assert payload.get("pagination").get("total") is not None
    assert payload.get("pagination").get("page") is not None
    assert payload.get("pagination").get("per_page") is not None
    assert payload.get("pagination").get("pages") is not None
    assert "has_next" in payload.get("pagination")
    assert "has_prev" in payload.get("pagination")
    assert "prev_num" in payload.get("pagination")
    assert "next_num" in payload.get("pagination")

def test_get_device_not_found(client, users):
    with logged_user(client, users["admin_user"]):
        response = client.get(url_for("individuals.device", id_tracking_device=-1))
    assert response.status_code == 404

def test_get_device_returns_payload(client, users, devices):
    with logged_user(client, users["admin_user"]):
        response = client.get(url_for("individuals.device", id_tracking_device=devices.id_tracking_device))
    assert response.status_code == 200
    assert response.get_json()["id_tracking_device"] == devices.id_tracking_device
