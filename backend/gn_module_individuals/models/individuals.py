from apptax.taxonomie.models import Taxref
from geonature.core.gn_monitoring.models import TIndividuals
from geonature.core.gn_synthese.models import Synthese
from geonature.utils.env import DB
from pypnnomenclature.models import TNomenclatures as Nomenclature
from sqlalchemy import select, inspect


def _add_mapper_property(name, prop):
    if not hasattr(TIndividuals, name):
        TIndividuals.__mapper__.add_property(name, prop)


def _register_nomenclatures_attribute():
    """Reproduces NomenclaturesMixin.__declare_last__ for TIndividuals.

    TIndividuals is a core model, so it can't inherit the mixin (which must be
    in the class bases at declaration time). Instead we set __nomenclatures__
    here to the list of TIndividuals relationships pointing to TNomenclatures,
    used by routes/individuals.py (eager loading + schema `only`), the same
    way gn_module_occhab does with Station.__nomenclatures__.
    """
    if hasattr(TIndividuals, "__nomenclatures__"):
        return
    mapper = inspect(TIndividuals)
    TIndividuals.__nomenclatures__ = [
        key for key, rel in mapper.relationships.items() if rel.entity.class_ == Nomenclature
    ]


def register_individual_extensions():
    _add_mapper_property(
        "taxon",
        DB.relationship(
            Taxref,
            primaryjoin=TIndividuals.cd_nom == Taxref.cd_nom,
            foreign_keys=[TIndividuals.cd_nom],
            lazy="select",
            viewonly=True,
        ),
    )
    _register_nomenclatures_attribute()


# ---------------------------------------------------------------------------
# An individual's last observation (position, date, observers) is read from
# gn_synthese.synthese (fed by Occtax's real-time trigger and by manual sync
# of Monitoring sub-modules), not computed here.
# ---------------------------------------------------------------------------


def _individual_last_synthese_column(column):
    return (
        select(column)
        .where(Synthese.id_individual == TIndividuals.id_individual)
        .order_by(Synthese.date_max.desc())
        .limit(1)
        .correlate(TIndividuals)
        .scalar_subquery()
    )


def individual_last_observation_geom_expression():
    return _individual_last_synthese_column(Synthese.the_geom_point)


def individual_last_observation_date_expression():
    return _individual_last_synthese_column(Synthese.date_max)


def individual_last_observation_observers_expression():
    return _individual_last_synthese_column(Synthese.observers)
