from geonature.utils.env import DB
from flask import g
from pypnnomenclature.models import TNomenclatures
from pypnnomenclature.utils import NomenclaturesMixin
from geonature.core.gn_monitoring.models import TIndividuals
from pypnusershub.db.models import User
from sqlalchemy.dialects.postgresql import JSONB

from .devices import TrackingDevices


class IndividualDeployments(NomenclaturesMixin, DB.Model):
    __tablename__ = "t_individual_deployments"
    __table_args__ = {"schema": "gn_individual"}

    id_deployment = DB.Column(
        "id_deployment",
        DB.Integer,
        primary_key=True,
        autoincrement=True,
    )

    id_capture = DB.Column(
        "id_capture",
        DB.Integer,
        DB.ForeignKey("gn_individual.t_captures.id_capture"),
        nullable=False,
    )

    id_individual = DB.Column(
        "id_individual",
        DB.Integer,
        DB.ForeignKey("gn_monitoring.t_individuals.id_individual"),
        nullable=False,
    )

    id_nomenclature_deployment_type = DB.Column(
        "id_nomenclature_deployment_type",
        DB.Integer,
        DB.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
        nullable=False,
    )

    id_nomenclature_deployment_location = DB.Column(
        "id_nomenclature_deployment_location",
        DB.Integer,
        DB.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
        nullable=False,
    )

    id_tracking_device = DB.Column(
        "id_tracking_device",
        DB.Integer,
        DB.ForeignKey("gn_individual.bib_tracking_devices.id_tracking_device"),
        nullable=True,
    )

    marking_code = DB.Column(
        "marking_code",
        DB.Text,
        nullable=True,
    )

    install_date = DB.Column(
        "install_date",
        DB.DateTime,
        nullable=False,
    )

    removal_date = DB.Column(
        "removal_date",
        DB.DateTime,
        nullable=True,
    )

    comment = DB.Column(
        "comment",
        DB.Text,
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

    individual = DB.relationship(
        TIndividuals,
        primaryjoin=TIndividuals.id_individual == id_individual,
        foreign_keys=[id_individual],
        lazy="select",
        back_populates="deployments",
    )

    tracking_device = DB.relationship(
        TrackingDevices,
        primaryjoin=TrackingDevices.id_tracking_device == id_tracking_device,
        foreign_keys=[id_tracking_device],
        lazy="select",
        back_populates="deployments",
    )

    capture = DB.relationship(
        "IndividualCaptures",
        primaryjoin="IndividualDeployments.id_capture == IndividualCaptures.id_capture",
        foreign_keys=[id_capture],
        lazy="select",
        back_populates="deployments",
    )

    nomenclature_deployment_type = DB.relationship(
        TNomenclatures,
        primaryjoin=(TNomenclatures.id_nomenclature == id_nomenclature_deployment_type),
        foreign_keys=[id_nomenclature_deployment_type],
        lazy="select",
    )

    nomenclature_deployment_location = DB.relationship(
        TNomenclatures,
        primaryjoin=(TNomenclatures.id_nomenclature == id_nomenclature_deployment_location),
        foreign_keys=[id_nomenclature_deployment_location],
        lazy="select",
    )

    digitiser = DB.relationship(
        User,
        primaryjoin=(User.id_role == id_digitiser),
        foreign_keys=[id_digitiser],
        lazy="select",
    )

    @classmethod
    def register_individual_backref(cls):
        """Attaches TIndividuals.deployments from the module side, once both classes exist."""
        if not hasattr(TIndividuals, "deployments"):
            TIndividuals.deployments = DB.relationship(
                cls,
                primaryjoin=cls.id_individual == TIndividuals.id_individual,
                foreign_keys=[cls.id_individual],
                lazy="select",
                viewonly=True,
            )

    def has_instance_permission(self, scope):
        if scope == 0:
            return False
        elif scope in (1, 2):
            return g.current_user == self.digitiser
        elif scope == 3:
            return True
