import json

from flask import request, g, make_response
from marshmallow import EXCLUDE, ValidationError

from geonature.core.gn_permissions import decorators as permissions
from geonature.core.gn_permissions.decorators import login_required
from geonature.utils.env import db
from utils_flask_sqla.response import json_resp

from .. import MODULE_CODE
from ..blueprint import blueprint
from ..models import IndividualDeployments
from ..schemas import DeploymentWriteSchema
from ..utils.errors import APIError, ApiErrorCode


@blueprint.route("/deployments", methods=["POST"])
@login_required
@permissions.check_cruved_scope(
    "C", get_scope=True, module_code=MODULE_CODE, object_code="INDIVIDUALS"
)
@json_resp
def create_deployment(scope):
    """
    Post one new deployment

    .. :quickref: Deployments;

    Expects a JSON body matching ``DeploymentWriteSchema``, including
    ``id_individual``.

    :returns: the created deployment
    :rtype: dict<IndividualDeployments>
    """
    data = request.get_json(silent=True)

    if not data:
        raise APIError(
            ApiErrorCode.MISSING_JSON_BODY,
            "Missing JSON request body.",
            400,
        )

    schema = DeploymentWriteSchema(unknown=EXCLUDE)
    try:
        deployment = schema.load(data)
    except ValidationError as e:
        raise APIError(
            ApiErrorCode.VALIDATION_ERROR,
            f"Validation failed: {json.dumps(e.messages)}",
            400,
        )

    deployment.id_digitiser = g.current_user.id_role

    db.session.add(deployment)
    db.session.commit()

    return schema.dump(deployment), 201


@blueprint.route("/deployments/<int(signed=True):id_deployment>", methods=["PUT"])
@login_required
@permissions.check_cruved_scope(
    "U", get_scope=True, module_code=MODULE_CODE, object_code="INDIVIDUALS"
)
@json_resp
def update_deployment(id_deployment, scope):
    """
    Update one deployment

    .. :quickref: Deployments;

    Expects a JSON body matching ``DeploymentWriteSchema``.

    :param id_deployment: the id_deployment
    :type id_deployment: int

    :returns: the updated deployment
    :rtype: dict<IndividualDeployments>
    """
    deployment = db.session.get(IndividualDeployments, id_deployment)
    if deployment is None:
        raise APIError(
            ApiErrorCode.NOT_FOUND,
            f"Deployment with id {id_deployment} was not found.",
            404,
            params={"id": id_deployment},
        )

    data = request.get_json(silent=True)
    if not data:
        raise APIError(
            ApiErrorCode.MISSING_JSON_BODY,
            "Missing JSON request body.",
            400,
        )

    if not deployment.has_instance_permission(scope):
        raise APIError(
            ApiErrorCode.INSUFFICIENT_PERMISSIONS,
            f"You do not have permission to update deployment {id_deployment}.",
            403,
        )

    schema = DeploymentWriteSchema(unknown=EXCLUDE)
    try:
        deployment = schema.load(data, instance=deployment)
    except ValidationError as e:
        raise APIError(
            ApiErrorCode.VALIDATION_ERROR,
            f"Validation failed: {json.dumps(e.messages)}",
            400,
        )

    deployment.id_digitiser = g.current_user.id_role

    db.session.commit()

    return schema.dump(deployment), 200


@blueprint.route("/deployments/<int(signed=True):id_deployment>", methods=["DELETE"])
@login_required
@permissions.check_cruved_scope(
    "D", get_scope=True, module_code=MODULE_CODE, object_code="INDIVIDUALS"
)
def delete_deployment(id_deployment, scope):
    """
    Delete one deployment

    .. :quickref: Deployments;

    :param id_deployment: the id_deployment
    :type id_deployment: int

    :returns: empty response
    """
    deployment = db.session.get(IndividualDeployments, id_deployment)
    if deployment is None:
        raise APIError(
            ApiErrorCode.NOT_FOUND,
            f"Deployment with id {id_deployment} was not found.",
            404,
            params={"id": id_deployment},
        )

    if not deployment.has_instance_permission(scope):
        raise APIError(
            ApiErrorCode.INSUFFICIENT_PERMISSIONS,
            f"You do not have permission to delete deployment {id_deployment}.",
            403,
        )

    db.session.delete(deployment)
    db.session.commit()
    return make_response("", 204)
