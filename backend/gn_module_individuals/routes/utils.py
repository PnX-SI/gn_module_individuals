"""Shared functions for export routes (individuals.py, devices.py)."""

import datetime
from pathlib import Path

import fiona
from fiona.crs import from_epsg
from flask import current_app

from geonature.utils import filemanager

from ..utils.errors import APIError, ApiErrorCode


def export_filename(prefix):
    timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%Hh%Mm%S")
    return filemanager.removeDisallowedFilenameChars(f"{prefix}_{timestamp}")


def check_export_format(export_format, entity_config):
    if export_format not in entity_config["EXPORT_FORMAT"]:
        raise APIError(
            ApiErrorCode.INVALID_FILTER,
            f"Unsupported export format '{export_format}'.",
            400,
        )


def write_geopackage(feature_collection, filename, srid):
    """Writes a FeatureCollection (as produced by GeoAlchemyAutoSchema with
    as_geojson=True) to a GeoPackage file.

    Every non-geometry property is written as a string: the exported columns
    are mostly computed labels (fields.Method)

    :param srid: SRID of the feature collection's geometries. Not looked up
        here: it depends on the caller's data source (e.g. individuals read
        theirs from gn_synthese.synthese.the_geom_point, always EPSG:4326),
        not something this generic writer should assume.
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
        crs=from_epsg(srid),
    ) as f:
        for feature in features:
            properties = {
                k: (str(v) if v is not None else None) for k, v in feature["properties"].items()
            }
            f.write({"geometry": feature["geometry"], "properties": properties})

    return str(dir_path), file_name
