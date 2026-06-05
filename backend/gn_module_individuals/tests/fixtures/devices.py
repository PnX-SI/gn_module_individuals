import pytest
from sqlalchemy import func, select

from geonature.tests.fixtures import *
from geonature.utils.env import db
from geonature.tests.utils import get_id_nomenclature

from gn_module_individuals.models import TrackingDevices

devices_example=[(('TYPE_DISPO_SUIVI',1), "Ornitela", "Balise 56", "2023-01-01", "2023-12-31", "admin_user", "admin_user", "commentaire test"),
                 (('TYPE_DISPO_SUIVI',2), "Lotek", "Balise 57", "2023-01-01", "2023-12-31", "self_user", "admin_user", "commentaire test"),
                 (('TYPE_DISPO_SUIVI',3), "Vifly", "Balise 58", "2023-01-01", "2023-12-31", "self_user", "self_user", "commentaire test"),
                 (('TYPE_DISPO_SUIVI',4), "Ornitela", "Balise 59", "2023-01-01", "2023-12-31", "admin_user", "self_user", "commentaire test")]

@pytest.fixture
def devices(users):
    db_devices = []

    for nomenclature, provider_name, provider_device_id, meta_create_date, meta_update_date, id_digitiser, id_referer, comment in devices_example:
        id_nomenclature_device_type=get_id_nomenclature(
            nomenclature_type_mnemonique=nomenclature[0], cd_nomenclature=str(nomenclature[1])
        ) 
        db_devices.append(
            TrackingDevices(
                id_nomenclature_device_type=id_nomenclature_device_type,
                provider_name = provider_name,
                provider_device_id = provider_device_id,
                meta_create_date = meta_create_date,
                meta_update_date = meta_update_date,
                id_digitiser=users[id_digitiser].id_role,
                id_referer=users[id_referer].id_role,
                comment=comment,
            )
        )
    # Insertion des individus dans la base de données
    with db.session.begin_nested():
        db.session.add_all(db_devices)
        db.session.flush()
    return db_devices


@pytest.fixture
def device():
    next_id = db.session.scalar(select(func.coalesce(func.max(TrackingDevices.id_tracking_device), 0))) + 1
    with db.session.begin_nested():
        instance = TrackingDevices(id_tracking_device=next_id)
        db.session.add(instance)
        db.session.flush()
    return instance
