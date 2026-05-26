import pytest
from sqlalchemy import select

from apptax.taxonomie.models import Taxref
from geonature.utils.env import db
from geonature.core.gn_monitoring.models import TIndividuals


@pytest.fixture
def individual(users):
    cd_nom = db.session.scalar(select(Taxref.cd_nom).limit(1))
    ind = TIndividuals(
        individual_name="Test Individual",
        cd_nom=cd_nom,
        id_digitiser=users["admin_user"].id_role,
    )
    with db.session.begin_nested():
        db.session.add(ind)
        db.session.flush()
    return ind
