"""
Définition des routes du module export
"""

# import logging

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import joinedload

from flask import Blueprint, request
from werkzeug.exceptions import NotFound, BadRequest

from geonature.core.gn_permissions import decorators as permissions
from geonature.core.gn_permissions.decorators import login_required
from geonature.utils.env import db
from utils_flask_sqla.response import json_resp

from . import MODULE_CODE

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
    return [
        {
            "items": 
            [
                {
                    "id_tracking_device": 1,
                    "id_nomenclature_device_type": 1,
                    "provider_name": "Ornitela",
                    "provider_device_id": "RG2345",
                    "id_referer": 123,
                    "comment": "Commentaire sur le dispositif",
                    "id_digitiser" : 123,
                    "meta_create_date" : "12-12-2026",
                    "meta_update_date" : "12-12-2026",
                    "nomenclature_device_type": {},
                    "referer_name": "Jackson Feblard",
                    "digitiser_name": "Jean Dupont",
                },
                {
                    "id_tracking_device": 2,
                    "id_nomenclature_device_type": 1,
                    "provider_name": "Ornitela",
                    "provider_device_id": "RG2147",
                    "id_referer": 123,
                    "comment": "Commentaire sur le dispositif",
                    "id_digitiser" : 123,
                    "meta_create_date" : "12-12-2026",
                    "meta_update_date" : "12-12-2026",
                    "nomenclature_device_type": {},
                    "referer_name": "Jackson Feblard",
                    "digitiser_name": "Jean Dupont",
                },
            ],
            "page": 0,
            "pages": 1,
            "per_page": 0,
            "prev_num": 0,
            "total": 0,
            "prev_num": 0,
            "next_num": 0,
            "has_next": 0,
            "has_prev": 0,
        }
    ]