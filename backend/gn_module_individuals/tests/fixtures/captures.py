import datetime as dt
import pytest
from sqlalchemy import func, select

from geonature.utils.env import db
from geonature.tests.utils import get_id_nomenclature

from gn_module_individuals.models.captures import Capture


def _capture_protocol(cd_nomenclature="1"):
    return get_id_nomenclature(
        nomenclature_type_mnemonique="PROTOCOLE_CAPTURE", cd_nomenclature=cd_nomenclature
    )


captures_example = [
    ("1", dt.datetime(2023, 1, 1), "admin_user", "commentaire test"),
    ("2", dt.datetime(2023, 2, 1), "self_user", "commentaire test"),
]


@pytest.fixture
def captures(users):
    db_captures = []
    for cd_nomenclature, date, id_digitiser, comment in captures_example:
        db_captures.append(
            Capture(
                id_nomenclature_capture_protocol=_capture_protocol(cd_nomenclature),
                date=date,
                geom_local=func.ST_SetSRID(func.ST_MakePoint(6.0, 45.0), 4326),
                id_digitiser=users[id_digitiser].id_role,
                comment=comment,
            )
        )
    with db.session.begin_nested():
        db.session.add_all(db_captures)
        db.session.flush()
    return db_captures


@pytest.fixture
def capture(users):
    with db.session.begin_nested():
        instance = Capture(
            id_nomenclature_capture_protocol=_capture_protocol("1"),
            date=dt.datetime(2023, 1, 1),
            geom_local=func.ST_SetSRID(func.ST_MakePoint(6.0, 45.0), 4326),
            id_digitiser=users["admin_user"].id_role,
            comment="commentaire test",
        )
        db.session.add(instance)
        db.session.flush()
    return instance
