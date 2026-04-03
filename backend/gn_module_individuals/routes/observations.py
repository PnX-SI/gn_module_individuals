
from geonature.utils.json import pagination_schema, MyJSONProvider
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import joinedload

from flask import  request, jsonify,g
from werkzeug.exceptions import NotFound, BadRequest

from geonature.core.gn_permissions import decorators as permissions
from geonature.core.gn_permissions.decorators import login_required
from geonature.utils.env import db
from utils_flask_sqla.response import json_resp

from ..blueprint import blueprint

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
