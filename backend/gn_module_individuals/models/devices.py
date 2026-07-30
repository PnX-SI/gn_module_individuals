from flask import g
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import false, or_

from geonature.utils.env import DB
from geonature.core.gn_monitoring.models import TIndividuals
from pypnusershub.db.models import User
from pypnnomenclature.models import TNomenclatures
from pypnnomenclature.utils import NomenclaturesMixin


class TrackingDevices(NomenclaturesMixin, DB.Model):
    __tablename__ = "bib_tracking_devices"
    __table_args__ = {"schema": "gn_individual"}

    id_tracking_device = DB.Column(
        DB.Integer,
        primary_key=True,
        autoincrement=True,
    )

    id_nomenclature_device_type = DB.Column(
        "id_nomenclature_device_type",
        DB.Integer,
        DB.ForeignKey(TNomenclatures.id_nomenclature),
    )

    provider_name = DB.Column(
        "provider_name",
        DB.Text,
    )

    provider_device_id = DB.Column(
        "provider_device_id",
        DB.Text,
    )

    id_referer = DB.Column(
        "id_referer",
        DB.Integer,
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
    )

    meta_create_date = DB.Column(
        "meta_create_date",
        DB.DateTime,
    )

    meta_update_date = DB.Column(
        "meta_update_date",
        DB.DateTime,
        nullable=True,
    )

    # Relationships
    nomenclature_device_type = DB.relationship(
        TNomenclatures,
        foreign_keys=[id_nomenclature_device_type],
    )

    referer = DB.relationship(
        User,
        primaryjoin=(User.id_role == id_referer),
        foreign_keys=[id_referer],
        lazy="select",
    )

    digitiser = DB.relationship(
        User,
        primaryjoin=(User.id_role == id_digitiser),
        foreign_keys=[id_digitiser],
        lazy="select",
    )

    deployments = DB.relationship(
        "IndividualDeployments",
        primaryjoin="TrackingDevices.id_tracking_device == IndividualDeployments.id_tracking_device",
        foreign_keys="IndividualDeployments.id_tracking_device",
        lazy="select",
        order_by="IndividualDeployments.install_date.desc()",
        back_populates="tracking_device",
    )

    @hybrid_property
    def organism_actors(self):
        """Organisms that own this device, through its digitiser and its referer.

        Mirrors TIndividuals.organism_actors so scope 2 behaves identically on
        both resources.
        """
        return [
            actor.id_organisme
            for actor in (self.digitiser, self.referer)
            if isinstance(actor, User)
        ]

    @classmethod
    def filter_by_scope(cls, query, scope, user=None):
        if user is None:
            user = g.current_user
        if scope == 0:
            query = query.where(false())
        elif scope in (1, 2):
            ors = [
                cls.id_digitiser == user.id_role,
                cls.id_referer == user.id_role,
            ]
            # if organism is None => do not filter on id_organism even if level = 2
            if scope == 2 and user.id_organisme is not None:
                ors.append(cls.digitiser.has(id_organisme=user.id_organisme))
                ors.append(cls.referer.has(id_organisme=user.id_organisme))
            query = query.where(or_(*ors))
        return query

    def has_instance_permission(self, scope):
        user = g.current_user
        # Nothing
        if scope == 0:
            return False
        # My data
        elif scope == 1:
            return user == self.digitiser or user == self.referer
        # My company's data
        elif scope == 2 and user.id_organisme is not None:
            return user.id_organisme in self.organism_actors
        # All
        elif scope == 3:
            return True
