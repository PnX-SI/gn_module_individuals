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


@pytest.fixture
def individuals(users):
    """Crée 3 individus : 2 actifs (admin + self) et 1 inactif (admin)."""
    cd_nom = db.session.scalar(select(Taxref.cd_nom).limit(1))
    inds = [
        TIndividuals(
            individual_name="Individu Actif Admin",
            cd_nom=cd_nom,
            active=True,
            id_digitiser=users["admin_user"].id_role,
        ),
        TIndividuals(
            individual_name="Individu Inactif Admin",
            cd_nom=cd_nom,
            active=False,
            id_digitiser=users["admin_user"].id_role,
        ),
        TIndividuals(
            individual_name="Individu Actif Self",
            cd_nom=cd_nom,
            active=True,
            id_digitiser=users["self_user"].id_role,
        ),
    ]
    with db.session.begin_nested():
        db.session.add_all(inds)
        db.session.flush()
    return inds
