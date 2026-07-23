from apptax.taxonomie.models import Taxref
from geoalchemy2 import Geometry
from geonature.core.gn_monitoring.models import TIndividuals
from geonature.utils.env import DB
from pypnnomenclature.models import TNomenclatures as Nomenclature
from sqlalchemy import func, case, inspect
from sqlalchemy.dialects.postgresql import INTERVAL


def _add_mapper_property(name, prop):
    if not hasattr(TIndividuals, name):
        TIndividuals.__mapper__.add_property(name, prop)


def _register_nomenclatures_attribute():
    """
    Équivalent de pypnnomenclature.utils.NomenclaturesMixin.__declare_last__,
    appliqué en surcouche : TIndividuals est un modèle core, on ne peut pas le
    faire hériter du mixin (qui doit être dans les bases à la déclaration de
    la classe). On reproduit donc son effet ici : __nomenclatures__ devient la
    liste des relations de TIndividuals pointant vers TNomenclatures, utilisée
    ensuite dans routes/individuals.py (eager loading + only du schéma),
    comme le fait gn_module_occhab avec Station.__nomenclatures__.
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
# TEMPORAIRE : tant que la jointure occtax (cor_counting_occtax.id_individual)
# n'est pas réintégrée, fonction qui génère une fausse "dernière observation"
# (position, date, observateurs), par individu  : simples expressions SQL,
#  assignées en attributs Python après coup via une requête annexe
#  — voir routes/individuals.py).
# À supprimer/remplacer dès que l'intégration réelle revient.
# ---------------------------------------------------------------------------

FAKE_OBSERVERS_POOL = ["Jean Dupont, Marie Martin", "Alice Durand", "Paul Bernard, Sophie Leroy"]


def temporary_individual_geom_expression():
    return func.ST_SetSRID(
        func.ST_MakePoint(
            6.0 + (func.mod(TIndividuals.id_individual, 1000) * 0.001),
            45.0 + (func.mod(TIndividuals.id_individual, 1000) * 0.001),
        ),
        4326,
        type_=Geometry("POINT", srid=4326),
    )


def temporary_individual_date_expression():
    days_ago = func.mod(TIndividuals.id_individual, 365)
    return func.now() - func.cast(func.concat(days_ago, " days"), INTERVAL)


def temporary_individual_observers_expression():
    idx = func.mod(TIndividuals.id_individual, len(FAKE_OBSERVERS_POOL))
    whens = [(idx == i, name) for i, name in enumerate(FAKE_OBSERVERS_POOL)]
    return case(*whens, else_=FAKE_OBSERVERS_POOL[0])
