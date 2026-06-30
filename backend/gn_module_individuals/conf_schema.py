"""
Toml Schema Specification for Configuration Parameters
"""

from marshmallow import Schema, fields


class GlobalSchema(Schema):
    ID_TAXON_LIST = fields.Integer(load_default=[])

class IndividualsSchema(Schema):
    DEFAULT_PAGE_SIZE = fields.Integer()
    DEFAULT_DISPLAYED_COLUMNS = fields.List(fields.String(), load_default=[])
    DEFAULT_DEPLOY_DISPLAYED_COLUMNS = fields.List(fields.String(), load_default=[])

class DevicesSchema(Schema):
    DEFAULT_PAGE_SIZE = fields.Integer()
    DEFAULT_DISPLAYED_COLUMNS = fields.List(fields.String(), load_default=[])
    DEFAULT_DEPLOY_DISPLAYED_COLUMNS = fields.List(fields.String(), load_default=[])

class GnModuleSchemaConf(Schema):
    GLOBAL = fields.Nested(GlobalSchema, load_default={})
    DEVICES = fields.Nested(DevicesSchema, load_default={})
    INDIVIDUALS = fields.Nested(IndividualsSchema, load_default={})
