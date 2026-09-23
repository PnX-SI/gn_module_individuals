"""Export routes for the individuals and devices lists.

Both routes export the entire currently filtered/sorted/scoped list (not a
selection of checked rows), bounded by the module's NB_MAX_EXPORT config.

Individuals additionally support GeoJSON and GeoPackage, using the
individual's last known observation position (from gn_synthese.synthese, see
models/individuals.py). That position is not a mapped column, only a Python
attribute assigned after the fact by _assign_last_observation(), so the list
is fully materialized before being serialized rather than streamed straight
from the query.
"""

import datetime
from pathlib import Path

import fiona
from fiona.crs import from_epsg
from flask import current_app, request, send_from_directory

from geonature.core.gn_permissions import decorators as permissions
from geonature.core.gn_permissions.decorators import login_required
from geonature.utils import filemanager
from geonature.utils.env import db
from utils_flask_sqla.response import to_csv_resp, to_json_resp

from .. import MODULE_CODE
from ..blueprint import blueprint
from ..schemas.devices import TrackingDeviceListSchema
from ..schemas.individuals import IndividualExportSchema
from ..utils.errors import APIError, ApiErrorCode
from .devices import _build_devices_query, _parse_device_filters
from .individuals import (
    _assign_last_observation,
    _build_individuals_query,
    _parse_filters,
    _parse_sort,
)

# gn_synthese.synthese.the_geom_point, the source of an individual's last
# observation position (see models/individuals.py), is stored in EPSG:4326.
INDIVIDUALS_GEOM_SRID = 4326


def _export_filename(prefix):
    timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%Hh%Mm%S")
    return filemanager.removeDisallowedFilenameChars(f"{prefix}_{timestamp}")


def _check_export_format(export_format, entity_config):
    if export_format not in entity_config["EXPORT_FORMAT"]:
        raise APIError(
            ApiErrorCode.INVALID_FILTER,
            f"Unsupported export format '{export_format}'.",
            400,
        )


def _write_geopackage(feature_collection, filename):
    """Writes a FeatureCollection (as produced by GeoAlchemyAutoSchema with
    as_geojson=True) to a GeoPackage file.

    Every non-geometry property is written as a string: the exported columns
    are mostly computed labels (fields.Method), not real table columns, so
    there is no reliable column type to introspect (unlike
    utils_flask_sqla_geo.export.export_geopackage, which infers property
    types from the schema's mapped table and can't be reused here for the
    same reason).
    """
    dir_path = Path(current_app.config["MEDIA_FOLDER"]) / "geopackages"
    dir_path.mkdir(parents=True, exist_ok=True)
    filemanager.delete_recursively(str(dir_path), excluded_files=[".gitkeep"])

    features = feature_collection["features"]
    property_names = features[0]["properties"].keys() if features else []
    gpkg_schema = {
        "geometry": "Unknown",
        "properties": {name: "str" for name in property_names},
    }

    file_name = f"{filename}.gpkg"
    with fiona.open(
        str(dir_path / file_name),
        "w",
        driver="GPKG",
        schema=gpkg_schema,
        crs=from_epsg(INDIVIDUALS_GEOM_SRID),
    ) as f:
        for feature in features:
            properties = {
                k: (str(v) if v is not None else None) for k, v in feature["properties"].items()
            }
            f.write({"geometry": feature["geometry"], "properties": properties})

    return str(dir_path), file_name


@blueprint.route("/individuals/export/<export_format>", methods=["POST"])
@login_required
# The "E" (Export) CRUVED action is not configured for this module yet, so
# exporting is gated on "R" instead: anyone who can read the list can export
# it. Once "E" is set up (permission admin UI), swap the two lines below.
@permissions.check_cruved_scope(
    "R", get_scope=True, module_code=MODULE_CODE, object_code="INDIVIDUALS"
)
# @permissions.check_cruved_scope(
#     "E", get_scope=True, module_code=MODULE_CODE, object_code="INDIVIDUALS"
# )
def export_individuals(export_format, scope):
    """
    Export the currently filtered individuals list

    .. :quickref: Individuals;

    The route is in POST to accept the same filters as GET /individuals
    without an overly long query string.

    :param export_format: ``csv``, ``geojson`` or ``gpkg`` (see the
        INDIVIDUALS.EXPORT_FORMAT module config)
    :type export_format: str

    :returns: a file attachment
    """
    entity_config = blueprint.config["INDIVIDUALS"]
    _check_export_format(export_format, entity_config)

    filters = _parse_filters(request.args)
    sort = _parse_sort(request.args)
    # eager_load=True (the default): the export schema reads the same
    # taxon/digitiser/nomenclature_sex relationships as IndividualListSchema.
    query = _build_individuals_query(scope, filters, sort).limit(entity_config["NB_MAX_EXPORT"])

    individuals = db.session.scalars(query).unique().all()
    _assign_last_observation(individuals)

    columns = entity_config["EXPORT_COLUMNS"] or None
    filename = _export_filename("individuals")

    if export_format == "csv":
        schema = IndividualExportSchema(only=columns)
        return to_csv_resp(
            filename,
            schema.dump(individuals, many=True),
            columns=list(schema.dump_fields.keys()),
            separator=";",
        )

    schema = IndividualExportSchema(as_geojson=True, feature_geometry="geom", only=columns)
    feature_collection = schema.dump(individuals, many=True)

    if export_format == "geojson":
        return to_json_resp(feature_collection, as_file=True, filename=filename, indent=4)

    dir_name, file_name = _write_geopackage(feature_collection, filename)
    return send_from_directory(dir_name, file_name, as_attachment=True)


@blueprint.route("/devices/export/<export_format>", methods=["POST"])
@login_required
# See export_individuals() above: gated on "R" until "E" is configured.
@permissions.check_cruved_scope(
    "R", get_scope=True, module_code=MODULE_CODE, object_code="INDIVIDUALS"
)
# @permissions.check_cruved_scope(
#     "E", get_scope=True, module_code=MODULE_CODE, object_code="INDIVIDUALS"
# )
def export_devices(export_format, scope):
    """
    Export the currently filtered devices list

    .. :quickref: Devices;

    The route is in POST to accept the same filters as GET /devices without
    an overly long query string.

    :param export_format: ``csv`` (see the DEVICES.EXPORT_FORMAT module config)
    :type export_format: str

    :returns: a file attachment
    """
    entity_config = blueprint.config["DEVICES"]
    _check_export_format(export_format, entity_config)

    filters = _parse_device_filters(request.args)
    # eager_load=True (the default): TrackingDeviceListSchema reads the same
    # nomenclature_device_type/digitiser/referer/deployments relationships as
    # list_devices().
    query = _build_devices_query(scope, filters).limit(entity_config["NB_MAX_EXPORT"])

    devices = db.session.scalars(query).unique().all()

    columns = entity_config["EXPORT_COLUMNS"] or None
    schema = TrackingDeviceListSchema(only=columns)
    return to_csv_resp(
        _export_filename("devices"),
        schema.dump(devices, many=True),
        columns=list(schema.dump_fields.keys()),
        separator=";",
    )
