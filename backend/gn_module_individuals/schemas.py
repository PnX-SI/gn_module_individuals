from geonature.utils.env import db, ma
from marshmallow import fields
from utils_flask_sqla.schema import SmartRelationshipsMixin

from .models import TrackingDevices,IndividualDeployments
from pypnnomenclature.schemas import NomenclatureSchema
from pypnusershub.schemas import UserSchema

class TrackingDevicesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TrackingDevices
        include_fk = True
        load_instance = True
        sqla_session = db.session
        include_relationships = True
        feature_id = "id_tracking_device"

    id_tracking_device = ma.auto_field(dump_only=True)
    nomenclature_device_type_name = fields.Method("get_nomenclature", dump_only=True)
    digitiser_name = fields.Method("get_digitiser", dump_only=True)
    referer_name = fields.Method("get_referer", dump_only=True)
    meta_create_date = fields.Date(format="%Y-%m-%d", dump_only=True)
    meta_update_date = fields.Date(format="%Y-%m-%d", dump_only=True)
    last_individual_equipped_name = fields.Method("get_last_individual_equipped_name", dump_only=True)
    deployments = ma.Nested("IndividualDeploymentsSchema", many=True)

    def get_nomenclature(self, obj):
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

    # def get_last_individual_equipped_name(self, obj):
    #     if obj.deployments:
    #         last_deployment = obj.deployments[0]
    #         if last_deployment.individual:
    #             return last_deployment.individual.individual_name
    #     return None

    def get_last_individual_equipped_name(self, obj):
        if not obj.deployments:
            return None
        
        if obj.deployments:
            last_deployment = obj.deployments[0]

        if last_deployment.individual:
            individual = last_deployment.individual
            name = individual.individual_name

            if individual.taxon and individual.taxon.nom_vern:
                return f"{name} ({individual.taxon.nom_vern})"

            return name

class IndividualDeploymentsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = IndividualDeployments
        include_fk = True
        load_instance = True
        sqla_session = db.session
        include_relationships = True
        feature_id = "id_deployment"

    id_deployment = ma.auto_field(dump_only=True)

    nomenclature_deployment_type = fields.Method("get_deployment_type", dump_only=True)
    nomenclature_deployment_location = fields.Method("get_deployment_location", dump_only=True)
    install_date  = fields.DateTime(format="%Y-%m-%d", dump_only=True)
    removal_date  = fields.DateTime(format="%Y-%m-%d", dump_only=True)
    meta_create_date = fields.Date(format="%Y-%m-%d", dump_only=True)
    meta_update_date = fields.Date(format="%Y-%m-%d", dump_only=True)
    individual_name = fields.Method("get_individual_name", dump_only=True)
    tracking_device_info = fields.Method("get_tracking_device", dump_only=True)
    name_digitiser = fields.Method("get_digitiser", dump_only=True)

    def get_deployment_type(self, obj):
        if obj.nomenclature_deployment_type:
            return obj.nomenclature_deployment_type.label_fr
        return None

    def get_deployment_location(self, obj):
        if obj.nomenclature_deployment_location:
            return obj.nomenclature_deployment_location.label_fr
        return None

    # def get_individual_name(self, obj):
    #     if obj.individual:
    #         return obj.individual.individual_name
    #     return None

    def get_individual_name(self, obj):
        if obj.individual:
            name = obj.individual.individual_name
            if obj.individual.taxon and obj.individual.taxon.nom_vern:
                return f"{name} ({obj.individual.taxon.nom_vern})"
            return name
        return None

    def get_tracking_device(self, obj):
        if obj.tracking_device:
            return f"{obj.tracking_device.provider_name} - {obj.tracking_device.provider_device_id}"
        return None

    def get_digitiser(self, obj):
        if obj.digitiser:
            return f"{obj.digitiser.prenom_role} {obj.digitiser.nom_role}"
        return None