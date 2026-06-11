from geonature.utils.env import db, ma
from marshmallow import fields, validates, validates_schema, ValidationError
from utils_flask_sqla.schema import SmartRelationshipsMixin

from geonature.utils.schema import CruvedSchemaMixin
from pypnnomenclature.utils import NomenclaturesConverter
from pypnnomenclature.models import TNomenclatures
from pypnusershub.schemas import UserSchema
from pypnusershub.db.models import User
from geonature.core.gn_monitoring.models import TIndividuals

from .. import MODULE_CODE
from ..models import TrackingDevices, IndividualDeployments
from .utils import get_label


class IndividualDeploymentsSchema(SmartRelationshipsMixin, ma.SQLAlchemyAutoSchema):
    class Meta:
        model = IndividualDeployments
        include_fk = True
        load_instance = True
        sqla_session = db.session
        include_relationships = True
        model_converter = NomenclaturesConverter
        feature_id = "id_deployment"

    id_deployment = ma.auto_field(dump_only=True)
    install_date = fields.DateTime(format="%Y-%m-%d", dump_only=True)
    removal_date = fields.DateTime(format="%Y-%m-%d", dump_only=True)
    meta_create_date = fields.Date(format="%Y-%m-%d", dump_only=True)
    meta_update_date = fields.Date(format="%Y-%m-%d", dump_only=True)

    nomenclature_deployment_type = fields.Method("get_deployment_type", dump_only=True)
    nomenclature_deployment_location = fields.Method("get_deployment_location", dump_only=True)
    individual_name = fields.Method("get_individual_name", dump_only=True)
    tracking_device_info = fields.Method("get_tracking_device", dump_only=True)
    name_digitiser = fields.Method("get_digitiser", dump_only=True)

    __module_code__ = MODULE_CODE

    # Validators

    @validates("id_individual")
    def validate_individual(self, value, **kwargs):
        if db.session.get(TIndividuals, value) is None:
            raise ValidationError(f"L'individu {value} n'existe pas.")
        return value

    @validates("id_tracking_device")
    def validate_tracking_device(self, value, **kwargs):
        if db.session.get(TrackingDevices, value) is None:
            raise ValidationError(f"Le dispositif de suivi {value} n'existe pas.")
        return value

    @validates("id_nomenclature_deployment_type")
    def validate_nomenclature_deployment_type(self, value, **kwargs):
        if value is None:
            return value
        if db.session.get(TNomenclatures, value) is None:
            raise ValidationError(f"La nomenclature {value} (type de déploiement) n'existe pas.")
        return value

    @validates("id_nomenclature_deployment_location")
    def validate_nomenclature_deployment_location(self, value, **kwargs):
        if value is None:
            return value
        if db.session.get(TNomenclatures, value) is None:
            raise ValidationError(
                f"La nomenclature {value} (localisation du déploiement) n'existe pas."
            )
        return value

    @validates_schema
    def validate_dates(self, data, **kwargs):
        """removal_date doit être postérieure à install_date si les deux sont présentes."""
        install = data.get("install_date")
        removal = data.get("removal_date")
        if install and removal and removal <= install:
            raise ValidationError(
                {"removal_date": ["removal_date doit être postérieure à install_date."]}
            )

    # Serialisation

    def get_deployment_type(self, obj):
        if obj.nomenclature_deployment_type:
            return get_label(obj.nomenclature_deployment_type)
        return None

    def get_deployment_location(self, obj):
        if obj.nomenclature_deployment_location:
            returnget_label(obj.nomenclature_deployment_location)
        return None

    def get_individual_name(self, obj):
        if obj.individual:
            name = obj.individual.individual_name
            if obj.individual.taxon and obj.individual.taxon.nom_vern:
                return f"{name} ({obj.individual.taxon.nom_vern})"
            return name
        return None

    def get_tracking_device(self, obj):
        if obj.tracking_device:
            return (
                f"{obj.tracking_device.provider_name}"
                f" - {obj.tracking_device.provider_device_id}"
            )
        return None

    def get_digitiser(self, obj):
        if obj.digitiser:
            return f"{obj.digitiser.prenom_role} {obj.digitiser.nom_role}"
        return None
