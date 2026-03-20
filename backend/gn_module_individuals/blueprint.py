"""
Définition des routes du module individus
"""

# import logging

from geonature.utils.json import pagination_schema, MyJSONProvider
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import joinedload

from flask import Blueprint, request, jsonify,g
from werkzeug.exceptions import NotFound, BadRequest

from geonature.core.gn_permissions import decorators as permissions
from geonature.core.gn_permissions.decorators import login_required
from geonature.utils.env import db
from utils_flask_sqla.response import json_resp

from . import MODULE_CODE
from .schemas import TrackingDevicesSchema
from .models import TrackingDevices

# A utiliser pour stocker les logs dans le fichier de log
# logger = logging.getLogger(__name__)
blueprint = Blueprint("individuals", __name__, cli_group="individuals")

## ########################################################################
## ENTITY - GET
## ########################################################################
@blueprint.route("/individuals", methods=["GET"])
@login_required
@json_resp
def list_individuals():
    geojson = {
        "features": [
            {
                "geometry": {
                    "coordinates": [
                        -1.363055012466776,
                        -5.983571570298366
                    ],
                    "type": "Point"
                },
                "id": 0,
                "properties": {
                    "additional_data": {
                        "collier": "vert/rouge",
                        "taille_cm": 40.2
                    },
                    "cd_nom": 2962,
                    "id_individual": 4,
                    "id_nomenclature_sex": 165,
                    "name": "Crâne d'oeuf",
                    "nomenclature_sex": {},
                    "taxref": {}
                },
                "type": "Feature"
            }
        ],
        "type": "FeatureCollection"
    }

    return {
        "total": len(geojson["features"]),   # or real pagination values
        "page": 0,
        "items": geojson
    }

@blueprint.route("/observations", methods=["GET"])
@login_required
@json_resp
def list_observations():
    geojson = {
        "features": [
            {
                "geometry": {
                    "coordinates": [
                        -1.363055012466776,
                        -5.983571570298366
                    ],
                    "type": "Point"
                },
                "id": 0,
                "properties": {
                    "id_observation": 1,
                },
                "type": "Feature"
            }
        ],
        "type": "FeatureCollection"
    }
    
    return {
        "total": len(geojson["features"]),
        "page": 0,
        "items": geojson
    }

@blueprint.route("/captures", methods=["GET"])
@login_required
@json_resp
def list_captures():
    geojson = {
        "features": [
            {
                "geometry": {
                    "coordinates": [
                        -1.363055012466776,
                        -5.983571570298366
                    ],
                    "type": "Point"
                },
                "id": 0,
                "properties": {
                    "id_capture": 1,
                },
                "type": "Feature"
            }
        ],
        "type": "FeatureCollection"
    }

    return {
        "total": len(geojson["features"]),
        "page": 0,
        "items": geojson
    }

@blueprint.route("/devices", methods=["GET"])
@login_required
@json_resp
def list_devices():

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    schema = TrackingDevicesSchema(many=True)

    query = (
         db.select(TrackingDevices)
         .options(
             joinedload(TrackingDevices.nomenclature_device_type),
             joinedload(TrackingDevices.digitiser),
             joinedload(TrackingDevices.referer),
         )
    )
   
    pagination = db.paginate(query, page=page, per_page=per_page, error_out=False)
    return {
        "items": schema.dump(pagination.items),
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "prev_num": pagination.prev_num,
            "next_num": pagination.next_num,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        }
    }


@blueprint.route("/devices/<int(signed=True):id_tracking_device>", methods=["GET"])
@login_required
@json_resp
def device(id_tracking_device):
    query = (
        db.select(TrackingDevices)
        .options(
            joinedload(TrackingDevices.nomenclature_device_type),
            joinedload(TrackingDevices.digitiser),
            joinedload(TrackingDevices.referer),
        )
        .where(TrackingDevices.id_tracking_device == id_tracking_device)
    )

    device = db.session.execute(query).unique().scalar_one_or_none()

    if device is None:
        return None, 404
    return TrackingDevicesSchema().dump(device)
   