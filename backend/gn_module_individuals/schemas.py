from geonature.utils.env import db, ma
from marshmallow import fields
from utils_flask_sqla.schema import SmartRelationshipsMixin

from .models import TrackingDevices
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
    nomenclature_device_type = fields.Method("get_nomenclature", dump_only=True)
    name_digitiser = fields.Method("get_digitiser", dump_only=True)
    name_referer = fields.Method("get_referer", dump_only=True)

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
