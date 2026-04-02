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
    per_page = request.args.get("per_page", type=int, default=5)
    page = request.args.get("page", type=int, default=1)
    items = [
                {
                    "comment": "Test balise GPS/Lotek",
                    "id_digitiser": 5,
                    "id_nomenclature_device_type": 628,
                    "id_referer": 4,
                    "id_tracking_device": 5,
                    "meta_create_date": "10-03-2025",
                    "meta_update_date": "21-03-2026",
                    "digitiser_name": "test Partenaire",
                    "referer_name": "test Agent",
                    "nomenclature_device_type_name": "Balise GPS",
                    "provider_device_id": "18256-9G",
                    "provider_name": "Lotek",
                    "last_individual_equipped_name": "Tartampion (Bouquetin des Alpes)",
                },
                {
                    "comment": "Test balise GPS/GSM",
                    "id_digitiser": 4,
                    "id_nomenclature_device_type": 628,
                    "id_referer": 3,
                    "id_tracking_device": 6,
                    "meta_create_date": "10-03-2026",
                    "meta_update_date": "21-03-2026",
                    "digitiser_name": "test Agent",
                    "referer_name": "test Administrateur",
                    "nomenclature_device_type_name": "Balise GPS",
                    "provider_device_id": "182A256ATXG",
                    "provider_name": "GSM Provider",
                    "last_individual_equipped_name":[]
                },
                {
                    "comment": "Test balise GPS",
                    "id_digitiser": 4,
                    "id_nomenclature_device_type": 628,
                    "id_referer": 4,
                    "id_tracking_device": 7,
                    "meta_create_date": "10-03-2026",
                    "meta_update_date": "21-03-2026",
                    "digitiser_name": "test Agent",
                    "referer_name": "test Agent",
                    "nomenclature_device_type_name": "Balise GPS",
                    "provider_device_id": "182243",
                    "provider_name": "Ornitela",
                    "last_individual_equipped_name": "Starbuck (Tétras Lyre)",
                },
                {
                    "comment": "Test balise GPS/Lotek",
                    "id_digitiser": 5,
                    "id_nomenclature_device_type": 628,
                    "id_referer": 4,
                    "id_tracking_device": 8,
                    "meta_create_date": "10-03-2026",
                    "meta_update_date": "21-03-2026",
                    "digitiser_name": "test Partenaire",
                    "referer_name": "test Agent",
                    "nomenclature_device_type_name": "Balise GPS",
                    "provider_device_id": "121256-AZ",
                    "provider_name": "Lotek",
                    "last_individual_equipped_name":[]
                },
                {
                    "comment": "Test balise GPS/GSM",
                    "id_digitiser": 4,
                    "id_nomenclature_device_type": 628,
                    "id_referer": 3,
                    "id_tracking_device": 9,
                    "meta_create_date": "10-03-2026",
                    "meta_update_date": "21-03-2026",
                    "digitiser_name": "test Agent",
                    "referer_name": "test Administrateur",
                    "nomenclature_device_type_name": "Balise GPS",
                    "provider_device_id": "182A256ARG",
                    "provider_name": "GSM Provider",
                    "last_individual_equipped_name":[]
                },
                {
                    "comment": "Test balise GPS",
                    "id_digitiser": 4,
                    "id_nomenclature_device_type": 628,
                    "id_referer": 4,
                    "id_tracking_device": 10,
                    "meta_create_date": "11-03-2023",
                    "meta_update_date": "21-03-2026",
                    "digitiser_name": "test Agent",
                    "referer_name": "test Agent",
                    "nomenclature_device_type_name": "Balise GPS",
                    "provider_device_id": "182243",
                    "provider_name": "Ornitela",
                    "last_individual_equipped_name":[]
                },
                {
                    "comment": "Test balise GSM/Ornitela",
                    "id_digitiser": 4,
                    "id_nomenclature_device_type": 629,
                    "id_referer": 6,
                    "id_tracking_device": 11,
                    "meta_create_date": "10-03-2026",
                    "meta_update_date": "21-03-2026",
                    "digitiser_name": "test Agent",
                    "referer_name": "Pierre Paul",
                    "nomenclature_device_type_name": "Balise GSM",
                    "provider_device_id": "182A9P6ARP-6",
                    "provider_name": "Ornitela",
                    "last_individual_equipped_name":[]
                },
                {
                    "comment": "Test balise GSM/Lotek",
                    "id_digitiser": 6,
                    "id_nomenclature_device_type": 629,
                    "id_referer": 3,
                    "id_tracking_device": 12,
                    "meta_create_date": "10-03-2026",
                    "meta_update_date": "21-03-2026",
                    "digitiser_name": "Pierre Paul",
                    "referer_name": "test Administrateur",
                    "nomenclature_device_type_name": "Balise GSM",
                    "provider_device_id": "18256-9G",
                    "provider_name": "Lotek",
                    "last_individual_equipped_name":[]
                },
                {
                    "comment": "Test balise GSM",
                    "id_digitiser": 6,
                    "id_nomenclature_device_type": 629,
                    "id_referer": 4,
                    "id_tracking_device": 13,
                    "meta_create_date": "10-03-2026",
                    "meta_update_date": "21-03-2026",
                    "digitiser_name": "Pierre Paul",
                    "referer_name": "test Agent",
                    "nomenclature_device_type_name": "Balise GSM",
                    "provider_device_id": "182A256POX",
                    "provider_name": "GSM Provider",
                    "last_individual_equipped_name":[]
                },
                {
                    "comment": "Test balise GSM/Ornitela",
                    "id_digitiser": 4,
                    "id_nomenclature_device_type": 629,
                    "id_referer": 6,
                    "id_tracking_device": 14,
                    "meta_create_date": "31-03-2026",
                    "meta_update_date": None,
                    "digitiser_name": "Pascal Véronique",
                    "referer_name": "Pascal Véronique",
                    "nomenclature_device_type_name": "Balise GSM",
                    "provider_device_id": "182A256ARG",
                    "provider_name": "Ornitela",
                    "last_individual_equipped_name":[]
                }
            ]
    
    return {
        "items": items[per_page * (page - 1):per_page * page],
        "has_next": True if page * per_page < len(items) else False,
        "has_prev": False if page == 1 else True,
        "next_num": page + 1 if page * per_page < len(items) else None,
        "page": page,
        "pages": (len(items) + per_page - 1) // per_page,
        "per_page": per_page,
        "prev_num": page - 1 if page > 1 else None,
        "total": len(items),
    }