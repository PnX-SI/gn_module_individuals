from flask import request, jsonify, g, make_response
from marshmallow import EXCLUDE, ValidationError

from sqlalchemy import func
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.exc import IntegrityError

from geonature.core.gn_permissions import decorators as permissions
from geonature.core.gn_permissions.decorators import login_required
from geonature.utils.env import db
from utils_flask_sqla.response import json_resp

from pypnnomenclature.schemas import NomenclatureSchema
from ..utils.errors import APIError, DevicesErrorCode

from .. import MODULE_CODE
from ..schemas import (
    TrackingDevicesDetailSchema,
    TrackingDevicesListSchema,
    TrackingDevicesWriteSchema,
)
from ..models import TrackingDevices, IndividualDeployments

from ..blueprint import blueprint


@blueprint.route("/devices/<int(signed=True):id_tracking_device>", methods=["GET"])
@login_required
@permissions.check_cruved_scope("R", get_scope=True, module_code=MODULE_CODE)
@json_resp
def device(id_tracking_device, scope):
    # Build nomenclatures fields list to serialize
    nomenclatures = list(TrackingDevices.__nomenclatures__)
    nomenclatures_fields = [n for n in nomenclatures]

    schema = TrackingDevicesDetailSchema(only=["+cruved", "referer"] + nomenclatures_fields)

    query = (
        db.select(TrackingDevices)
        .options(
            joinedload(TrackingDevices.nomenclature_device_type),
            selectinload(TrackingDevices.digitiser),
            selectinload(TrackingDevices.referer),
            joinedload(TrackingDevices.deployments).joinedload(IndividualDeployments.individual),
        )
        .where(TrackingDevices.id_tracking_device == id_tracking_device)
    )

    device = db.session.execute(query).unique().scalar_one_or_none()

    if device is None:
        raise APIError(
            DeviceErrorCode.DEVICE_NOT_FOUND,
            f"Tracking device with id {id_tracking_device} was not found.",
            404,
        )
    return schema.dump(device)


@blueprint.route("/devices", methods=["GET"])
@login_required
@permissions.check_cruved_scope("R", get_scope=True, module_code=MODULE_CODE)
@json_resp
def list_devices(scope):
    # Build nomenclatures fields list to serialize
    nomenclatures = list(TrackingDevices.__nomenclatures__)
    nomenclatures_fields = [n for n in nomenclatures]

    # Scope not yet used -------------
    device_type = request.args.get("type", type=int)
    provider_name = request.args.get("providerName", type=str)
    provider_id = request.args.get("providerDeviceId", type=str)

    page = request.args.get("page", type=int)
    per_page = request.args.get("per_page", type=int)

    prop = request.args.get("prop", type=str, default="meta_create_date")
    dir = request.args.get("dir", type=str, default="desc")

    paginated = page is not None and per_page is not None

    schema = TrackingDevicesListSchema(only=["+cruved", "referer"] + nomenclatures_fields)

    sort_col = getattr(TrackingDevices, prop, None)

    query = (
        db.select(TrackingDevices)
        .options(
            joinedload(TrackingDevices.nomenclature_device_type),
            selectinload(TrackingDevices.digitiser),
            selectinload(TrackingDevices.referer),
            joinedload(TrackingDevices.deployments).joinedload(IndividualDeployments.individual),
        )
        .order_by(sort_col.desc() if dir == "desc" else sort_col.asc())
    )

    if device_type is not None:
        query = query.where(TrackingDevices.id_nomenclature_device_type == device_type)
    if provider_name:
        query = query.where(TrackingDevices.provider_name.ilike(f"%{provider_name}%"))
    if provider_id:
        query = query.where(TrackingDevices.provider_device_id.ilike(f"%{provider_id}%"))

    if paginated:
        pagination = db.paginate(query, page=page, per_page=per_page, error_out=False)
        return {
            "items": schema.dump(pagination.items, many=True),
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "prev_num": pagination.prev_num,
            "next_num": pagination.next_num,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        }
    else:
        items = db.session.execute(query).unique().scalars().all()
        return schema.dump(items, many=True)


@blueprint.route("/devices", methods=["POST"])
@login_required
@permissions.check_cruved_scope(
    "C", get_scope=True, module_code=MODULE_CODE, object_code="INDIVIDUALS_INDIVIDUALS"
)
@json_resp
def create_device(scope):
    data = request.get_json()

    if not data:
        raise APIError(
            DeviceErrorCode.MISSING_JSON_BODY,
            "Missing JSON request body.",
            400,
        )

    schema = TrackingDevicesWriteSchema(unknown=EXCLUDE)
    try:
        device = schema.load(data)
    except ValidationError as e:
        raise APIError(
            DeviceErrorCode.VALIDATION_ERROR,
            f"Validation failed: {json.dumps(e.messages)}",
            400,
        )

    device.id_digitiser = g.current_user.id_role

    db.session.add(device)
    db.session.commit()

    return schema.dump(device), 201


@blueprint.route("/devices/<int(signed=True):id_tracking_device>", methods=["PUT"])
@login_required
@permissions.check_cruved_scope(
    "U", get_scope=True, module_code=MODULE_CODE, object_code="INDIVIDUALS_INDIVIDUALS"
)
@json_resp
def update_device(id_tracking_device, scope):
    device = db.session.get(TrackingDevices, id_tracking_device)
    if device is None:
        raise APIError(
            DeviceErrorCode.DEVICE_NOT_FOUND,
            f"Tracking device with id {id_tracking_device} was not found.",
            404,
        )
    data = request.get_json()

    if not data:
        raise APIError(
            DeviceErrorCode.MISSING_JSON_BODY,
            "Missing JSON request body.",
            400,
        )
    if not device.has_instance_permission(scope):
        raise APIError(
            DeviceErrorCode.INSUFFICIENT_PERMISSIONS,
            f"You do not have permission to update device {id_tracking_device}.",
            403,
        )

    schema = TrackingDevicesWriteSchema(unknown=EXCLUDE)
    try:
        device = schema.load(data, instance=device)
    except ValidationError as e:
        raise APIError(
            DeviceErrorCode.VALIDATION_ERROR,
            f"Validation failed: {json.dumps(e.messages)}",
            400,
        )

    device.id_digitiser = g.current_user.id_role

    db.session.commit()

    return schema.dump(device), 200


@blueprint.route("/devices/<int(signed=True):id_tracking_device>", methods=["DELETE"])
@login_required
@permissions.check_cruved_scope(
    "D", get_scope=True, module_code=MODULE_CODE, object_code="INDIVIDUALS_INDIVIDUALS"
)
def delete_device(id_tracking_device, scope):
    device = db.session.get(TrackingDevices, id_tracking_device)
    if device is None:
        raise APIError(
            DeviceErrorCode.DEVICE_NOT_FOUND,
            f"Tracking device with id {id_tracking_device} was not found.",
            404,
        )

    deployment_count = db.session.scalar(
        db.select(func.count())
        .select_from(IndividualDeployments)
        .where(IndividualDeployments.id_tracking_device == id_tracking_device)
    )
    if deployment_count:
        raise APIError(
            DeviceErrorCode.DEVICE_HAS_DEPLOYMENTS,
            "This device cannot be deleted because it is associated with deployments.",
            409,
            params={"id": id_tracking_device, "nb": deployment_count},
        )

    db.session.delete(device)
    db.session.commit()
    return make_response("", 204)
