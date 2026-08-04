from geonature.utils.env import db, ma
from marshmallow import fields, validates, validates_schema, ValidationError
from utils_flask_sqla.schema import SmartRelationshipsMixin

from geonature.utils.schema import CruvedSchemaMixin
from pypnnomenclature.utils import NomenclaturesConverter
from pypnnomenclature.models import TNomenclatures
from pypnnomenclature.schemas import NomenclatureSchema
from pypnusershub.schemas import UserSchema
from pypnusershub.db.models import User
from geonature.core.gn_monitoring.models import TIndividuals

from .. import MODULE_CODE
from ..models import TrackingDevices, IndividualDeployments
from .deployments import DeploymentSummarySchema
from .utils import get_label
from ..utils.errors import APIError, ApiErrorCode


class TrackingDevicesBaseSchema(
    CruvedSchemaMixin, SmartRelationshipsMixin, ma.SQLAlchemyAutoSchema
):
    """Raw columns plus computed labels. No relationships exposed: see
    TrackingDevicesDetailSchema for the full nested objects."""

    class Meta:
        model = TrackingDevices
        include_fk = True
        load_instance = True
        sqla_session = db.session
        include_relationships = False
        model_converter = NomenclaturesConverter
        feature_id = "id_tracking_device"

    __module_code__ = MODULE_CODE
    __object_code__ = "INDIVIDUALS"

    id_tracking_device = ma.auto_field(dump_only=True)
    meta_create_date = fields.Date(format="%Y-%m-%d", dump_only=True)
    meta_update_date = fields.Date(format="%Y-%m-%d", dump_only=True)
    comment = ma.auto_field()

    nomenclature_device_type_name = fields.Method("get_nomenclature_name", dump_only=True)
    digitiser_name = fields.Method("get_digitiser_name", dump_only=True)
    referer_name = fields.Method("get_referer_name", dump_only=True)

    # Validators

    @validates("provider_name")
    def validate_provider_name(self, value, **kwargs):
        if not value or not value.strip():
            raise APIError(
                ApiErrorCode.VALIDATION_ERROR,
                "The provider name can't be empty",
                400,
            )
        return value

    @validates("provider_device_id")
    def validate_provider_device_id(self, value, **kwargs):
        if not value or not value.strip():
            raise APIError(
                ApiErrorCode.VALIDATION_ERROR,
                "The provider device id can't be empty",
                400,
            )
        return value

    @validates("id_nomenclature_device_type")
    def validate_nomenclature_device_type(self, value, **kwargs):
        if value is None:
            return value
        exists = db.session.execute(
            db.select(TNomenclatures).filter_by(id_nomenclature=value)
        ).scalar_one_or_none()
        if exists is None:
            raise APIError(
                ApiErrorCode.VALIDATION_ERROR,
                f"The #{value} nomenclature is not found in configured nomenclatures",
                400,
            )
        return value

    @validates("id_referer")
    def validate_referer(self, value, **kwargs):
        if value is None:
            return value
        user = db.session.execute(db.select(User).filter_by(id_role=value)).scalar_one_or_none()
        if user is None:
            raise APIError(
                ApiErrorCode.VALIDATION_ERROR,
                f"The #{value} referer (user) do not exist.",
                400,
            )
        return value

    # Serialization

    def get_nomenclature_name(self, obj):
        if obj.nomenclature_device_type:
            return get_label(obj.nomenclature_device_type)
        return None

    def get_digitiser_name(self, obj):
        if obj.digitiser:
            return f"{obj.digitiser.prenom_role} {obj.digitiser.nom_role}"
        return None

    def get_referer_name(self, obj):
        if obj.referer:
            return f"{obj.referer.prenom_role} {obj.referer.nom_role}"
        return None


class TrackingDevicesListSchema(TrackingDevicesBaseSchema):
    """Adds only computed fields on top of the base: no relationships."""

    __module_code__ = MODULE_CODE
    __object_code__ = "INDIVIDUALS"

    last_individual_equipped_name = fields.Method(
        "get_last_individual_equipped_name", dump_only=True
    )

    def get_last_individual_equipped_name(self, obj):
        if not obj.deployments:
            return None
        last_deployment = obj.deployments[0]
        if last_deployment.individual:
            individual = last_deployment.individual
            name = individual.individual_name
            if individual.taxon and individual.taxon.nom_vern:
                return f"{name} ({individual.taxon.nom_vern})"
            return name
        return None


class TrackingDevicesDetailSchema(TrackingDevicesBaseSchema):
    """All of the model's relationships, in addition to the base fields."""

    __module_code__ = MODULE_CODE
    __object_code__ = "INDIVIDUALS"

    nomenclature_device_type = fields.Nested(NomenclatureSchema, dump_only=True)
    referer = fields.Nested(UserSchema, dump_only=True)
    digitiser = fields.Nested(UserSchema, dump_only=True)
    deployments = fields.Method("get_deployments", dump_only=True)

    def get_deployments(self, obj):
        if not obj.deployments:
            return []
        return DeploymentSummarySchema(many=True).dump(obj.deployments)


class TrackingDevicesWriteSchema(TrackingDevicesBaseSchema):
    class Meta(TrackingDevicesBaseSchema.Meta):
        exclude = (
            "nomenclature_device_type_name",
            "referer_name",
            "digitiser_name",
        )
