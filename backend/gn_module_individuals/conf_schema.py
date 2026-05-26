"""
Toml Schema Specification for Configuration Parameters
"""

from marshmallow import Schema, fields

class DevicesSchema(Schema):
    DEFAULT_DISPLAYED_COLUMNS = fields.List(
        fields.String(),
        load_default=[]
    )
    DEFAULT_DEPLOY_DISPLAYED_COLUMNS = fields.List(
        fields.String(),
        load_default=[]
    )

class GnModuleSchemaConf(Schema):
  DEVICES = fields.Nested(DevicesSchema, load_default={})