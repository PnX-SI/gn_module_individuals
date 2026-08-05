import datetime as dt
import pytest

from geonature.utils.env import db
from geonature.tests.utils import get_id_nomenclature

from gn_module_individuals.models import IndividualDeployments


def _make_deployment(individual, digitiser, install_date, **kwargs):
    dep = IndividualDeployments(
        id_individual=individual.id_individual,
        id_nomenclature_deployment_type=get_id_nomenclature(
            nomenclature_type_mnemonique="TYPE_MARQUAGE", cd_nomenclature="4"
        ),
        id_nomenclature_deployment_location=get_id_nomenclature(
            nomenclature_type_mnemonique="LOC_MARQUAGE", cd_nomenclature="3"
        ),
        install_date=install_date,
        id_digitiser=digitiser.id_role,
        **kwargs,
    )
    with db.session.begin_nested():
        db.session.add(dep)
        db.session.flush()
    return dep


@pytest.fixture
def deployment(individual, users):
    """A deployment digitised by admin_user."""
    return _make_deployment(individual, users["admin_user"], dt.datetime(2024, 1, 1))


@pytest.fixture
def deployment_by_self(individual, users):
    """A deployment digitised by self_user, used to test scope=1 permissions."""
    return _make_deployment(individual, users["self_user"], dt.datetime(2024, 2, 1))
