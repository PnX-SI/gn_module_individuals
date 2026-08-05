import json
from geonature.utils.env import db, ma
from pypnnomenclature.utils import NomenclaturesConverter
from marshmallow import fields, ValidationError
from utils_flask_sqla.schema import SmartRelationshipsMixin
from geoalchemy2.shape import from_shape, to_shape
from geojson import Feature
from utils_flask_sqla_geo.utilsgeometry import remove_third_dimension

from geonature.utils.schema import CruvedSchemaMixin
from geonature.utils.env import MA
from shapely.geometry import shape
from .. import MODULE_CODE
from ..models import Capture
from utils_flask_sqla_geo.schema import GeometryField, GeoModelConverter, GeoAlchemyAutoSchema


# PATCH : To move in utils_flask_sqla_geo
class GeojsonSerializationField(fields.Field):

    def _serialize(self, value, attr, obj):
        if value is None:
            return value
        else:
            if type(value).__name__ == "WKBElement":
                feature = Feature(geometry=to_shape(value))
                return feature.geometry
            else:
                return None

    def _deserialize(self, value, attr, data, **kwargs):
        if not value:
            return None
        try:
            if isinstance(value, str):
                value = json.loads(value)
            shape_ = shape(value)
            two_dimension_geom = remove_third_dimension(shape_)
            return from_shape(two_dimension_geom, srid=4326)
        except Exception as error:
            raise ValidationError("Geometry error") from error


class CapturesSchema(MA.SQLAlchemyAutoSchema, CruvedSchemaMixin, SmartRelationshipsMixin):
    class Meta:
        model = Capture
        include_fk = True
        load_instance = True
        sqla_session = db.session
        include_relationships = False
        model_converter = NomenclaturesConverter
        exclude = ("geom_4326",)

    __module_code__ = MODULE_CODE

    meta_create_date = fields.DateTime(format="%d-%m-%Y", dump_only=True)
    meta_update_date = fields.DateTime(format="%d-%m-%Y", dump_only=True, allow_none=True)
    geom_local = GeojsonSerializationField(required=False, allow_none=True)


class CaptureMapConverter(NomenclaturesConverter, GeoModelConverter):
    pass


class CaptureMapSchema(SmartRelationshipsMixin, GeoAlchemyAutoSchema):
    class Meta:
        model = Capture
        include_fk = False
        load_instance = True
        sqla_session = db.session
        feature_id = "id_capture"
        feature_geometry = "geom_local"
        model_converter = CaptureMapConverter

    geom_local = GeometryField(metadata={"exclude": True}, dump_only=True)
