from geonature.utils.json import pagination_schema, MyJSONProvider
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import joinedload

from flask import request, jsonify, g, make_response
from werkzeug.exceptions import Forbidden, NotFound, BadRequest

from geonature.core.gn_permissions import decorators as permissions
from geonature.core.gn_permissions.decorators import login_required
from geonature.utils.env import db
from utils_flask_sqla.response import json_resp
from marshmallow import EXCLUDE, fields, Schema
from sqlalchemy import select

from gn_module_individuals.schemas.captures import CaptureMapSchema, CapturesSchema
from gn_module_individuals import MODULE_CODE
from gn_module_individuals.models.captures import Capture, IndividualsCaptureObservations

from ..blueprint import blueprint
from ..utils.errors import APIError, ApiErrorCode

default_object_code = "INDIVIDUALS"


@blueprint.route("/captures", methods=["GET"])
@permissions.check_cruved_scope("R", get_scope=True, module_code=MODULE_CODE, object_code="ALL")
@login_required
def list_captures(scope):
    args = request.args

    individual_ids = args.getlist("individual_id", type=int)

    query = select(Capture)

    if len(individual_ids) > 0:
        query = query.join(
            IndividualsCaptureObservations,
            Capture.id_capture == IndividualsCaptureObservations.id_capture,
        )
        query = query.where(IndividualsCaptureObservations.id_individual.in_(individual_ids))

    results = db.session.scalars(select(Capture)).all()
    return CapturesSchema(many=True).dump(results)


@blueprint.route("/captures/geometry", methods=["GET"])
@login_required
@permissions.check_cruved_scope("R", get_scope=True, module_code=MODULE_CODE)
def capture_geometry(scope):
    # filters = _parse_filters(request.args)
    sort = {"prop": "id_individual", "dir": "asc"}
    query = select(Capture)
    query = Capture.filter_by_scope(query, scope)

    schema = CaptureMapSchema(
        many=True,
        as_geojson=True,
    )
    individuals = db.session.scalars(query).unique().all()
    return schema.dump(individuals)


@blueprint.route("/captures/<int(signed=True):id_capture>", methods=["DELETE"])
@login_required
@permissions.check_cruved_scope(
    "D", get_scope=True, module_code=MODULE_CODE, object_code=default_object_code
)
def delete_capture(scope, id_capture):
    cap = db.session.get(Capture, id_capture)
    if cap is None:
        raise APIError(
            ApiErrorCode.NOT_FOUND,
            f"Capture with id {id_capture} was not found.",
            404,
        )
    if not cap.has_instance_permission(scope):
        raise Forbidden()
    db.session.delete(cap)
    db.session.commit()
    return make_response("", 204)


@blueprint.route("/captures/<int(signed=True):id_capture>", methods=["GET"])
@login_required
@permissions.check_cruved_scope("R", get_scope=True, module_code=MODULE_CODE, object_code="ALL")
def get_capture_by_id(scope, id_capture):
    cap = db.session.get(Capture, id_capture)
    if cap is None:
        raise APIError(
            ApiErrorCode.NOT_FOUND,
            f"Capture with id {id_capture} was not found.",
            404,
        )
    if not cap.has_instance_permission(scope):
        raise Forbidden()

    serialized_cap = CapturesSchema().dump(cap)
    return jsonify(serialized_cap)


@blueprint.route("/captures", methods=["POST"])
@login_required
@permissions.check_cruved_scope("C", module_code=MODULE_CODE, object_code=default_object_code)
def post_capture():

    post_data = request.get_json(silent=True)
    if not "id_digitiser" in post_data:
        post_data["id_digitiser"] = g.current_user.id_role

    schema = CapturesSchema()
    capture = schema.load(post_data, unknown=EXCLUDE)

    db.session.add(capture)
    db.session.commit()
    return schema.dump(capture), 201


@blueprint.route("/captures/<int(signed=True):id_capture>", methods=["PATCH"])
@login_required
@permissions.check_cruved_scope(
    "U", get_scope=True, module_code=MODULE_CODE, object_code=default_object_code
)
def patch_capture(id_capture, scope):
    post_data = request.get_json(silent=True)
    if not "id_capture" in post_data:
        post_data["id_capture"] = id_capture
    capture = db.session.get(Capture, id_capture)
    if capture is None:
        raise APIError(
            ApiErrorCode.NOT_FOUND,
            f"Capture with id {id_capture} was not found.",
            404,
        )
    if not capture.has_instance_permission(scope):
        raise Forbidden(f"The user cannot modify this capture ! ")
    capture_ma = CapturesSchema().load(post_data)
    db.session.add(capture_ma)
    db.session.commit()
    return CapturesSchema().dump(capture_ma)
