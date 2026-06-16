from geonature.utils.env import DB
from flask import g
from sqlalchemy.dialects.postgresql import JSONB
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
        # DB.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
        DB.ForeignKey(TNomenclatures.id_nomenclature),
    )

    provider_name = DB.Column(
        "provider_name",
        DB.Text,
        nullable=True,
    )

    provider_device_id = DB.Column(
        "provider_device_id",
        DB.Text,
        nullable=True,
    )

    id_referer = DB.Column(
        "id_referer",
        DB.Integer,
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
    )

    meta_create_date = DB.Column(
        "meta_create_date",
        DB.DateTime,
    )

    meta_update_date = DB.Column(
        "meta_update_date",
        DB.DateTime,
    )

    # Relationships
    nomenclature_device_type = DB.relationship(
        TNomenclatures,
        # primaryjoin=(TNomenclatures.id_nomenclature == id_nomenclature_device_type),
        foreign_keys=[id_nomenclature_device_type],
        # lazy="select",
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

    def has_instance_permission(self, scope):
        if scope == 0:
            return False
        elif scope in (1, 2):
            return g.current_user == self.digitiser or g.current_user == self.referer
        elif scope == 3:
            return True
