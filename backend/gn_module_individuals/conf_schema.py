"""
Toml Schema Specification for Configuration Parameters
"""

from marshmallow import Schema, fields


class AdditionalFieldSchema(Schema):
    CD_NOM = fields.Integer(required=True)
    DATASET_SHORT_NAME = fields.String(required=True)
    ID_DATASET = fields.Integer(required=True)


class GlobalSchema(Schema):
    ID_TAXON_LIST = fields.Integer(load_default=None)
    SELECTED_LAYER_COLOR = fields.String(load_default="#d7191c")
    UNSELECTED_LAYER_COLOR = fields.String(load_default="#007bff")


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
    TAXON_DATASET = fields.List(fields.Nested(AdditionalFieldSchema), load_default=list)
    MAX_OBS_NB = fields.Integer(load_default=20)
    FIRST_LAYER_COLOR = fields.String(load_default="#fa9a00")
    EXPORT_FORMAT = fields.List(
        fields.String(),
        load_default=["csv", "geojson", "gpkg"],
    )
    NB_MAX_EXPORT = fields.Integer(load_default=50000)
    EXPORT_COLUMNS = fields.List(
        fields.String(),
        load_default=[
            "id_individual",
            "individual_name",
            "taxref_cd_nom",
            "taxref_nom_vern",
            "nomenclature_sex_name",
            "active",
            "digitiser_name",
            "last_observation_date",
            "last_observation_observers_name",
        ],
    )


class ObservationsSchema(Schema):
    DEFAULT_PAGE_SIZE = fields.Integer(load_default=10)
    LIST_COLUMNS = fields.List(
        fields.String(),
        load_default=["nom_vern_or_lb_nom", "date_min", "observers", "dataset_name"],
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
    EXPORT_FORMAT = fields.List(
        fields.String(),
        load_default=["csv"],
    )
    NB_MAX_EXPORT = fields.Integer(load_default=50000)
    EXPORT_COLUMNS = fields.List(
        fields.String(),
        load_default=[
            "id_tracking_device",
            "provider_name",
            "provider_device_id",
            "nomenclature_device_type_name",
            "referer_name",
            "last_individual_equipped_name",
            "digitiser_name",
            "meta_create_date",
        ],
    )


class GnModuleSchemaConf(Schema):
    GLOBAL = fields.Nested(GlobalSchema, load_default=GlobalSchema().load({}))
    INDIVIDUALS = fields.Nested(IndividualsSchema, load_default=IndividualsSchema().load({}))
    OBSERVATIONS = fields.Nested(ObservationsSchema, load_default=ObservationsSchema().load({}))
    DEVICES = fields.Nested(DevicesSchema, load_default=DevicesSchema().load({}))
