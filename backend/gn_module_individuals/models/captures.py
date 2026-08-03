from geoalchemy2 import Geometry

from geonature.utils.env import DB
from geonature.core.gn_monitoring.models import TIndividuals
from pypnusershub.db.models import User
from pypnnomenclature.models import TNomenclatures
from pypnnomenclature.utils import NomenclaturesMixin
from sqlalchemy.dialects.postgresql import JSONB


class IndividualCaptures(NomenclaturesMixin, DB.Model):
    __tablename__ = "t_captures"
    __table_args__ = {"schema": "gn_individual"}

    id_capture = DB.Column(
        "id_capture",
        DB.Integer,
        primary_key=True,
        autoincrement=True,
    )

    id_nomenclature_capture_protocol = DB.Column(
        "id_nomenclature_capture_protocol",
        DB.Integer,
        DB.ForeignKey(TNomenclatures.id_nomenclature),
        nullable=True,
    )

    comment = DB.Column(
        "comment",
        DB.Text,
        nullable=True,
    )

    date = DB.Column(
        "date",
        DB.DateTime,
        nullable=False,
    )

    geom_local = DB.Column(
        "geom_local",
        Geometry("POINT"),
        nullable=False,
    )

    geom_4326 = DB.Column(
        "geom_4326",
        Geometry("POINT", 4326),
        nullable=False,
    )

    additional_data = DB.Column(
        "additional_data",
        JSONB,
        nullable=True,
    )

    id_digitiser = DB.Column(
        "id_digitiser",
        DB.Integer,
        DB.ForeignKey("utilisateurs.t_roles.id_role"),
        nullable=True,
    )

    meta_create_date = DB.Column(
        "meta_create_date",
        DB.DateTime,
        nullable=True,
    )

    meta_update_date = DB.Column(
        "meta_update_date",
        DB.DateTime,
        nullable=True,
    )

    # Relationships
    nomenclature_capture_protocol = DB.relationship(
        TNomenclatures,
        foreign_keys=[id_nomenclature_capture_protocol],
    )

    digitiser = DB.relationship(
        User,
        primaryjoin=(User.id_role == id_digitiser),
        foreign_keys=[id_digitiser],
        lazy="select",
    )

    deployments = DB.relationship(
        "IndividualDeployments",
        primaryjoin="IndividualCaptures.id_capture == IndividualDeployments.id_capture",
        foreign_keys="IndividualDeployments.id_capture",
        lazy="select",
        back_populates="capture",
    )

    observations = DB.relationship(
        "IndividualsCaptureObservations",
        primaryjoin="IndividualCaptures.id_capture == IndividualsCaptureObservations.id_capture",
        foreign_keys="IndividualsCaptureObservations.id_capture",
        lazy="select",
        back_populates="capture",
    )

    observers = DB.relationship(
        User,
        secondary="gn_individual.cor_role_capture",
        lazy="select",
    )


class IndividualsCaptureObservations(DB.Model):
    __tablename__ = "t_individual_capture_observations"
    __table_args__ = {"schema": "gn_individual"}

    id_capture = DB.Column(
        "id_capture",
        DB.Integer,
        DB.ForeignKey("gn_individual.t_captures.id_capture"),
        primary_key=True,
    )

    id_individual = DB.Column(
        "id_individual",
        DB.Integer,
        DB.ForeignKey("gn_monitoring.t_individuals.id_individual"),
        primary_key=True,
    )

    additional_data = DB.Column(
        "additional_data",
        JSONB,
        nullable=True,
    )

    # Relationships
    capture = DB.relationship(
        IndividualCaptures,
        primaryjoin=(IndividualCaptures.id_capture == id_capture),
        foreign_keys=[id_capture],
        lazy="select",
        back_populates="observations",
    )

    individual = DB.relationship(
        TIndividuals,
        primaryjoin=(TIndividuals.id_individual == id_individual),
        foreign_keys=[id_individual],
        lazy="select",
        viewonly=True,
    )


cor_role_capture = DB.Table(
    "cor_role_capture",
    DB.Column(
        "id_capture",
        DB.Integer,
        DB.ForeignKey("gn_individual.t_captures.id_capture"),
        primary_key=True,
    ),
    DB.Column(
        "id_role",
        DB.Integer,
        DB.ForeignKey("utilisateurs.t_roles.id_role"),
        primary_key=True,
    ),
    schema="gn_individual",
)


class CorRoleCapture(DB.Model):
    __table__ = cor_role_capture
