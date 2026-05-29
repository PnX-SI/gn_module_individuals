from geonature.utils.json import pagination_schema, MyJSONProvider
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import joinedload,selectinload

from flask import request, jsonify, g, make_response
from marshmallow import EXCLUDE, ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Forbidden, NotFound, BadRequest, Conflict

from geonature.core.gn_permissions import decorators as permissions
from geonature.core.gn_permissions.decorators import login_required
from geonature.utils.env import db
from utils_flask_sqla.response import json_resp

from pypnnomenclature.schemas import NomenclatureSchema

from .. import MODULE_CODE
# from ..schemas import TrackingDevicesSchema
from ..schemas import TrackingDevicesDetailSchema, TrackingDevicesListSchema, TrackingDevicesWriteSchema
from ..models import TrackingDevices,IndividualDeployments

from ..blueprint import blueprint

@blueprint.route("/devices/<int(signed=True):id_tracking_device>", methods=["GET"])
@login_required
@permissions.check_cruved_scope("R", get_scope=True, module_code=MODULE_CODE)
@json_resp
def device(id_tracking_device, scope):
    query = (
        db.select(TrackingDevices)
        .options(
            joinedload(TrackingDevices.nomenclature_device_type),
            selectinload(TrackingDevices.digitiser),
            selectinload(TrackingDevices.referer),
            joinedload(TrackingDevices.deployments)
                .joinedload(IndividualDeployments.individual)
        )
        .where(TrackingDevices.id_tracking_device == id_tracking_device)
    )

    device = db.session.execute(query).unique().scalar_one_or_none()

    if device is None:
        raise NotFound(f"Le matériel de suivi {id_tracking_device} n'a pas été trouvé")

    # Claire version
    # return TrackingDevicesDetailSchema().dump(device)

    # Proposed version
    # SmartRelationshipsMixin have to get explicitely the relationship with only
    return TrackingDevicesDetailSchema(only=["nomenclature_device_type","referer"]).dump(device)

@blueprint.route("/devices", methods=["GET"])
@login_required
@permissions.check_cruved_scope("R", get_scope=True, module_code=MODULE_CODE)
@json_resp
def list_devices(scope):

    device_type    = request.args.get("type", type=int)
    provider_name  = request.args.get("providerName", type=str)
    provider_id    = request.args.get("providerDeviceId", type=str)

    page     = request.args.get("page", type=int)
    per_page = request.args.get("per_page", type=int)

    prop = request.args.get("prop", type=str, default="id_nomenclature_device_type")
    dir = request.args.get("dir", type=str, default="asc")

    paginated = page is not None and per_page is not None

    # Claire version
    # schema = TrackingDevicesSchema(exclude=("deployments",), many=True)

    # Proposed version
    schema = TrackingDevicesListSchema(many=True)

    sort_col = getattr(TrackingDevices, prop, None)

    query = (
        db.select(TrackingDevices)
        .options(
            joinedload(TrackingDevices.nomenclature_device_type),
            selectinload(TrackingDevices.digitiser),
            selectinload(TrackingDevices.referer),
            joinedload(TrackingDevices.deployments)
                .joinedload(IndividualDeployments.individual),
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
            "items": schema.dump(pagination.items),
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
        return schema.dump(items)


@blueprint.route("/devices", methods=["POST"])
@login_required
@permissions.check_cruved_scope("C", get_scope=True, module_code=MODULE_CODE)
@json_resp
def create_device(scope):
    data = request.get_json()
    if not data:
        raise BadRequest("Corps de requête JSON manquant.")

    schema = TrackingDevicesSchema(exclude=("deployments",), unknown=EXCLUDE)
    try:
        device = schema.load(data)
    except ValidationError as e:
        raise BadRequest(e.messages)

    device.id_digitiser = g.current_user.id_role

    db.session.add(device)
    db.session.commit()

    # Claire version
    # return TrackingDeviceDetailSchema().dump(device), 201
    # Proposed version
    return TrackingDevicesWriteSchema().dump(device), 201


@blueprint.route("/devices/<int(signed=True):id_tracking_device>", methods=["PUT"])
@login_required
@permissions.check_cruved_scope("U", get_scope=True, module_code=MODULE_CODE)
@json_resp
def update_device(id_tracking_device, scope):
    device = db.session.get(TrackingDevices, id_tracking_device)
    if device is None:
        raise NotFound(f"Le matériel de suivi {id_tracking_device} n'a pas été trouvé")
    
    data = request.get_json()
    if not data:
        raise BadRequest("Corps de requête JSON manquant.")
    if not device.has_instance_permission(scope):
        raise Forbidden(f"Vous n'avez pas la permission de mettre à jour le dispositif {id_tracking_device} ")
    
    schema = TrackingDevicesSchema(exclude=("deployments",), unknown=EXCLUDE)
    try:
        device = schema.load(data, instance=device)
    except ValidationError as e:
        raise BadRequest(e.messages)

    device.id_digitiser = g.current_user.id_role

    db.session.commit()

    # Claire version
    # return TrackingDeviceDetailSchema().dump(device)

    # Proposed version
    return TrackingDevicesWriteSchema().dump(device)


@blueprint.route("/devices/<int(signed=True):id_tracking_device>", methods=["DELETE"])
@login_required
@permissions.check_cruved_scope("D", get_scope=True, module_code=MODULE_CODE)
def delete_device(id_tracking_device, scope):
    device = db.session.get(TrackingDevices, id_tracking_device)
    if device is None:
        raise NotFound(f"Le matériel de suivi {id_tracking_device} n'a pas été trouvé")

    # !!!!!!! If there're deployments linked to this device, we cannot delete it.
    # Test to add

    if device.deployments:
        raise Conflict(
            "Ce dispositif ne peut pas être supprimé car il est utilisé dans des déploiements."
        )

    db.session.delete(device)
    db.session.commit()
    return make_response("", 204)