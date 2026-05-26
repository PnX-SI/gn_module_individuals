from geonature.utils.env import db, ma
from marshmallow import fields, validates, validates_schema, ValidationError
from utils_flask_sqla.schema import SmartRelationshipsMixin
from pypnnomenclature.utils import NomenclaturesConverter
from pypnnomenclature.models import TNomenclatures
from pypnusershub.db.models import User
from geonature.core.gn_monitoring.models import TIndividuals

from .models import TrackingDevices, IndividualDeployments

ADDITIONAL_DATA_ALLOWED_KEYS = ["removal_reason"]  # A RECUPERER DEPUIS LE FICHIER DE CONFIGURATION
class TrackingDevicesSchema(SmartRelationshipsMixin, ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TrackingDevices
        include_fk = True
        load_instance = True
        sqla_session = db.session
        include_relationships = True
        model_converter = NomenclaturesConverter
        feature_id = "id_tracking_device"

    id_tracking_device = ma.auto_field(dump_only=True)
    meta_create_date = fields.Date(format="%Y-%m-%d", dump_only=True)
    meta_update_date = fields.Date(format="%Y-%m-%d", dump_only=True)

    nomenclature_device_type_name = fields.Method("get_nomenclature_name", dump_only=True)
    digitiser_name = fields.Method("get_digitiser", dump_only=True)
    referer_name = fields.Method("get_referer", dump_only=True)
    last_individual_equipped_name = fields.Method(
        "get_last_individual_equipped_name", dump_only=True
    )

    deployments = ma.Nested("IndividualDeploymentsSchema", many=True)

    # Validators

    @validates("provider_name")
    def validate_provider_name(self, value, **kwargs):
        if not value or not value.strip():
            raise ValidationError("provider_name ne peut pas être vide.")
        return value

    @validates("provider_device_id")
    def validate_provider_device_id(self, value, **kwargs):
        if not value or not value.strip():
            raise ValidationError("provider_device_id ne peut pas être vide.")
        return value

    @validates("id_nomenclature_device_type")
    def validate_nomenclature_device_type(self, value, **kwargs):
        if value is None:
            return value
        exists = db.session.execute(
            db.select(TNomenclatures).filter_by(id_nomenclature=value)
        ).scalar_one_or_none()
        if exists is None:
            raise ValidationError(
                f"La nomenclature id={value} n'existe pas dans ref_nomenclatures."
            )
        return value

    @validates("id_referer")
    def validate_referer(self, value, **kwargs):
        if value is None:
            return value
        user = db.session.execute(
            db.select(User).filter_by(id_role=value)
        ).scalar_one_or_none()
        if user is None:
            raise ValidationError(f"L'utilisateur id_role={value} (référent) n'existe pas.")
        return value

    # Serialisation 

    def get_nomenclature_name(self, obj):
        if obj.nomenclature_device_type:
            return obj.nomenclature_device_type.label_fr
        return None

    def get_digitiser(self, obj):
        if obj.digitiser:
            return f"{obj.digitiser.prenom_role} {obj.digitiser.nom_role}"
        return None

    def get_referer(self, obj):
        if obj.referer:
            return f"{obj.referer.prenom_role} {obj.referer.nom_role}"
        return None

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

class DeploymentSummarySchema(ma.Schema):
    id_individual = fields.Integer(dump_only=True)
    individual_name = fields.Method("get_individual_name", dump_only=True)
    install_date = fields.DateTime(format="%d-%m-%y", dump_only=True)
    removal_date = fields.DateTime(format="%d-%m-%y", dump_only=True)
    comment = fields.Method("get_comment", dump_only=True)

    def get_individual_name(self, obj):
        if obj.individual:
            name = obj.individual.individual_name
            if obj.individual.taxon and obj.individual.taxon.nom_vern:
                return f"{name} ({obj.individual.taxon.nom_vern})"
            return name
        return None

    def get_comment(self, obj):
        if obj.comment:
            return obj.comment.replace("\n", "<br>")
        return None


class TrackingDeviceDetailSchema(ma.Schema):
    id_tracking_device = fields.Integer(dump_only=True)
    id_nomenclature_device_type = fields.Integer(dump_only=True)
    provider_name = fields.String(dump_only=True)
    provider_device_id = fields.String(dump_only=True)
    id_referer = fields.Integer(dump_only=True)
    id_digitiser = fields.Integer(dump_only=True)
    meta_create_date = fields.Date(format="%d-%m-%y", dump_only=True)
    meta_update_date = fields.Date(format="%d-%m-%y", dump_only=True)
    nomenclature_device_type_name = fields.Method("get_nomenclature_name", dump_only=True)
    referer_name = fields.Method("get_referer", dump_only=True)
    digitiser_name = fields.Method("get_digitiser", dump_only=True)
    comment = fields.Method("get_comment", dump_only=True)
    deployments = fields.Method("get_deployments", dump_only=True)

    def get_nomenclature_name(self, obj):
        if obj.nomenclature_device_type:
            return obj.nomenclature_device_type.label_fr
        return None

    def get_digitiser(self, obj):
        if obj.digitiser:
            return f"{obj.digitiser.prenom_role} {obj.digitiser.nom_role}"
        return None

    def get_referer(self, obj):
        if obj.referer:
            return f"{obj.referer.prenom_role} {obj.referer.nom_role}"
        return None

    def get_comment(self, obj):
        if obj.comment:
            return obj.comment.replace("\n", "<br>")
        return None

    def get_deployments(self, obj):
        if not obj.deployments:
            return []
        return DeploymentSummarySchema(many=True).dump(obj.deployments)


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

    # Validators
 
    @validates("id_individual")
    def validate_individual(self, value, **kwargs):
        individual = db.session.execute(
            db.select(TIndividuals).filter_by(id_individual=value)
        ).scalar_one_or_none()
        if individual is None:
            raise ValidationError(f"L'individu {value} n'existe pas.")
        return value

    @validates("id_tracking_device")
    def validate_tracking_device(self, value, **kwargs):
        device = db.session.execute(
            db.select(TrackingDevices).filter_by(id_tracking_device=value)
        ).scalar_one_or_none()
        if device is None:
            raise ValidationError(f"Le dispositif de suivi {value} n'existe pas.")
        return value

    @validates("id_nomenclature_deployment_type")
    def validate_nomenclature_deployment_type(self, value, **kwargs):
        if value is None:
            return value
        exists = db.session.execute(
            db.select(TNomenclatures).filter_by(id_nomenclature=value)
        ).scalar_one_or_none()
        if exists is None:
            raise ValidationError(
                f"La nomenclature {value} (type de déploiement) n'existe pas."
            )
        return value

    @validates("id_nomenclature_deployment_location")
    def validate_nomenclature_deployment_location(self, value, **kwargs):
        if value is None:
            return value
        exists = db.session.execute(
            db.select(TNomenclatures).filter_by(id_nomenclature=value)
        ).scalar_one_or_none()
        if exists is None:
            raise ValidationError(
                f"La nomenclature {value} (localisation du déploiement) n'existe pas."
            )
        return value

    @validates("additional_data")
    def validate_additional_data(self, value, **kwargs):
        if value is None:
            return value
        if not isinstance(value, dict):
            raise ValidationError("additional_data doit être un objet JSON (dict).")
        invalid_keys = set(value.keys()) - set(ADDITIONAL_DATA_ALLOWED_KEYS)
        if invalid_keys:
            raise ValidationError(
                f"Clés non autorisées dans additional_data : {sorted(invalid_keys)}. "
                f"Clés acceptées : {ADDITIONAL_DATA_ALLOWED_KEYS}."
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
            return obj.nomenclature_deployment_type.label_fr
        return None

    def get_deployment_location(self, obj):
        if obj.nomenclature_deployment_location:
            return obj.nomenclature_deployment_location.label_fr
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
