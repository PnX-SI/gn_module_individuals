
from geonature.utils.json import pagination_schema, MyJSONProvider
from sqlalchemy.dialects import postgresql

from flask import request, jsonify,g
from werkzeug.exceptions import NotFound, BadRequest

from geonature.core.gn_permissions import decorators as permissions
from geonature.core.gn_permissions.decorators import login_required
from geonature.utils.env import db
from utils_flask_sqla.response import json_resp


from ..blueprint import blueprint

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
