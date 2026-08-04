"""
Toml Schema Specification for Configuration Parameters
"""

from marshmallow import Schema, fields


class GlobalSchema(Schema):
    ID_TAXON_LIST = fields.Integer(load_default=100)
    SELECTED_LAYER_COLOR = fields.String()
    UNSELECTED_LAYER_COLOR = fields.String()
    SELECTED_LAYER_OPACITY = fields.Integer()
    UNSELECTED_LAYER_OPACITY = fields.Integer()


class IndividualsSchema(Schema):
    DEFAULT_PAGE_SIZE = fields.Integer(load_default=10)
    LIST_COLUMNS = fields.List(
        fields.String(),
        load_default=[
            "individual_name",
            "taxref_nom_vern",
            "nomenclature_sex_name",
            "last_observation_date",
            "active",
        ],
    )
    DEPLOYMENT_LIST_COLUMNS = fields.List(
        fields.String(),
        load_default=[
            "deployment_type_name",
            "deployment_location_name",
            "marking_code",
            "install_date",
            "removal_date",
        ],
    )


class DevicesSchema(Schema):
    DEFAULT_PAGE_SIZE = fields.Integer(load_default=10)
    LIST_COLUMNS = fields.List(
        fields.String(),
        load_default=[
            "provider_name",
            "provider_device_id",
            "nomenclature_device_type_name",
            "referer_name",
            "last_individual_equipped_name",
            "meta_create_date",
        ],
    )
    DEPLOYMENT_LIST_COLUMNS = fields.List(
        fields.String(),
        load_default=["individual_name", "install_date", "removal_date", "comment"],
    )


class GnModuleSchemaConf(Schema):
    GLOBAL = fields.Nested(GlobalSchema, load_default=GlobalSchema().load({}))
    DEVICES = fields.Nested(DevicesSchema, load_default=DevicesSchema().load({}))
    INDIVIDUALS = fields.Nested(IndividualsSchema, load_default=IndividualsSchema().load({}))
