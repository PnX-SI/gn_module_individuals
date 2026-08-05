import json

from flask import request, jsonify, make_response
from marshmallow import EXCLUDE, ValidationError
from sqlalchemy import select

from geonature.core.gn_permissions import decorators as permissions
from geonature.core.gn_permissions.decorators import login_required
from geonature.utils.env import db

from .. import MODULE_CODE
from ..blueprint import blueprint
from ..models.captures import Capture, IndividualsCaptureObservations
from ..schemas.captures import IndividualsCaptureObservationsSchema
from ..utils.errors import APIError, ApiErrorCode

default_object_code = "INDIVIDUALS"


def _get_observation_or_404(id_capture, id_individual):
    observation = db.session.get(IndividualsCaptureObservations, (id_capture, id_individual))
    if observation is None:
        raise APIError(
            ApiErrorCode.NOT_FOUND,
            f"Observation for capture {id_capture} and individual {id_individual}"
            " was not found.",
            404,
        )
    return observation


@blueprint.route("/observations", methods=["GET"])
@login_required
@permissions.check_cruved_scope("R", get_scope=True, module_code=MODULE_CODE, object_code="ALL")
def list_observations(scope):
    id_capture = request.args.get("id_capture", type=int)
    id_individual = request.args.get("id_individual", type=int)

    query = select(IndividualsCaptureObservations).join(
        Capture, Capture.id_capture == IndividualsCaptureObservations.id_capture
    )
    if id_capture is not None:
        query = query.where(IndividualsCaptureObservations.id_capture == id_capture)
    if id_individual is not None:
        query = query.where(IndividualsCaptureObservations.id_individual == id_individual)
    query = Capture.filter_by_scope(query, scope)

    observations = db.session.execute(query).unique().scalars().all()
    return jsonify(IndividualsCaptureObservationsSchema(many=True).dump(observations))


@blueprint.route(
    "/observations/<int(signed=True):id_capture>/<int(signed=True):id_individual>",
    methods=["GET"],
)
@login_required
@permissions.check_cruved_scope("R", get_scope=True, module_code=MODULE_CODE, object_code="ALL")
def get_observation(id_capture, id_individual, scope):
    observation = _get_observation_or_404(id_capture, id_individual)
    if not observation.capture.has_instance_permission(scope):
        raise APIError(
            ApiErrorCode.INSUFFICIENT_PERMISSIONS,
            "You do not have permission to read this observation.",
            403,
        )
    return jsonify(IndividualsCaptureObservationsSchema().dump(observation))


@blueprint.route("/observations", methods=["POST"])
@login_required
@permissions.check_cruved_scope(
    "C", get_scope=True, module_code=MODULE_CODE, object_code=default_object_code
)
def create_observation(scope):
    data = request.get_json(silent=True)
    if not data:
        raise APIError(
            ApiErrorCode.MISSING_JSON_BODY,
            "Missing JSON request body.",
            400,
        )

    id_capture = data.get("id_capture")
    capture = db.session.get(Capture, id_capture) if id_capture is not None else None
    if capture is None:
        raise APIError(
            ApiErrorCode.NOT_FOUND,
            f"Capture with id {id_capture} was not found.",
            404,
        )
    if not capture.has_instance_permission(scope):
        raise APIError(
            ApiErrorCode.INSUFFICIENT_PERMISSIONS,
            "You do not have permission to add observations to this capture.",
            403,
        )

    id_individual = data.get("id_individual")
    if db.session.get(IndividualsCaptureObservations, (id_capture, id_individual)) is not None:
        raise APIError(
            ApiErrorCode.VALIDATION_ERROR,
            f"Individual {id_individual} is already linked to capture {id_capture}.",
            400,
        )

    schema = IndividualsCaptureObservationsSchema(unknown=EXCLUDE)
    try:
        observation = schema.load(data)
    except ValidationError as e:
        raise APIError(
            ApiErrorCode.VALIDATION_ERROR,
            f"Validation failed: {json.dumps(e.messages)}",
            400,
        )

    db.session.add(observation)
    db.session.commit()
    return schema.dump(observation), 201


@blueprint.route(
    "/observations/<int(signed=True):id_capture>/<int(signed=True):id_individual>",
    methods=["PATCH"],
)
@login_required
@permissions.check_cruved_scope(
    "U", get_scope=True, module_code=MODULE_CODE, object_code=default_object_code
)
def update_observation(id_capture, id_individual, scope):
    observation = _get_observation_or_404(id_capture, id_individual)
    if not observation.capture.has_instance_permission(scope):
        raise APIError(
            ApiErrorCode.INSUFFICIENT_PERMISSIONS,
            "You do not have permission to update this observation.",
            403,
        )

    data = request.get_json(silent=True)
    if not data:
        raise APIError(
            ApiErrorCode.MISSING_JSON_BODY,
            "Missing JSON request body.",
            400,
        )

    schema = IndividualsCaptureObservationsSchema(unknown=EXCLUDE, partial=True)
    try:
        observation = schema.load(data, instance=observation, partial=True)
    except ValidationError as e:
        raise APIError(
            ApiErrorCode.VALIDATION_ERROR,
            f"Validation failed: {json.dumps(e.messages)}",
            400,
        )

    db.session.commit()
    return schema.dump(observation), 200


@blueprint.route(
    "/observations/<int(signed=True):id_capture>/<int(signed=True):id_individual>",
    methods=["DELETE"],
)
@login_required
@permissions.check_cruved_scope(
    "D", get_scope=True, module_code=MODULE_CODE, object_code=default_object_code
)
def delete_observation(id_capture, id_individual, scope):
    observation = _get_observation_or_404(id_capture, id_individual)
    if not observation.capture.has_instance_permission(scope):
        raise APIError(
            ApiErrorCode.INSUFFICIENT_PERMISSIONS,
            "You do not have permission to delete this observation.",
            403,
        )

    db.session.delete(observation)
    db.session.commit()
    return make_response("", 204)
