from flask import url_for
from pypnusershub.tests.utils import logged_user


# def test_list_devices_returns_paginated_list(client, users):
#     with logged_user(client, users["admin_user"]):
#         response = client.get(url_for("individuals.list_devices",page=1, per_page=10))
#     payload = response.get_json()
#     assert response.status_code == 200
#     assert isinstance(payload, dict)
#     assert payload.get("items") is not None
#     assert isinstance(payload.get("items"), list)
#     assert payload.get("total") is not None
#     assert payload.get("page") is not None
#     assert payload.get("per_page") is not None
#     assert payload.get("pages") is not None
#     assert payload.get("has_next") is not None
#     assert payload.get("has_prev") is not None
#     assert payload.get("prev_num") is not None
#     assert payload.get("next_num") is not None

def test_list_devices_without_pagination(client, users):
    with logged_user(client, users["admin_user"]):
        response = client.get(url_for("individuals.list_devices"))

    payload = response.get_json()
    assert response.status_code == 200
    assert isinstance(payload, list)

def test_get_device_not_found(client, users):
    with logged_user(client, users["admin_user"]):
        response = client.get(url_for("individuals.device", id_tracking_device=-1))
    assert response.status_code == 404

def test_get_device_returns_payload(client, users, device):
    with logged_user(client, users["admin_user"]):
        response = client.get(url_for("individuals.device", id_tracking_device=device.id_tracking_device))
    assert response.status_code == 200
    assert response.get_json()["id_tracking_device"] == device.id_tracking_device

def test_get_device_forbidden(client, users, device):
    with logged_user(client, users["noright_user"]):
        response = client.get(url_for("individuals.device", id_tracking_device=device.id_tracking_device))
    assert response.status_code == 403

def test_get_devices_filtering(client, users, devices):
    with logged_user(client, users["admin_user"]):
        response = client.get(url_for("individuals.list_devices", per_page=1))
    payload = response.get_json()

def test_device_fields(client, users):
    with logged_user(client, users["admin_user"]):
        response = client.get(
            url_for("individuals.list_devices", page=1, per_page=1)
        )

    payload = response.get_json()
    item = payload["items"][0]

    assert "id_tracking_device" in item
    assert "provider_name" in item