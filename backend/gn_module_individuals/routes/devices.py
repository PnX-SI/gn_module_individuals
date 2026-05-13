from geonature.utils.json import pagination_schema, MyJSONProvider
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import joinedload,selectinload  

from flask import request, jsonify,g
from werkzeug.exceptions import NotFound, BadRequest

from geonature.core.gn_permissions import decorators as permissions
from geonature.core.gn_permissions.decorators import login_required
from geonature.utils.env import db
from utils_flask_sqla.response import json_resp

from .. import MODULE_CODE
from ..schemas import TrackingDevicesSchema
from ..models import TrackingDevices,IndividualDeployments

from ..blueprint import blueprint

@blueprint.route("/devices", methods=["GET"])
@login_required
@permissions.check_cruved_scope("R", get_scope=True, module_code=MODULE_CODE)
@json_resp
def list_devices(scope):

    device_type    = request.args.get("type", type=int)
    provider_name  = request.args.get("providerName", type=str)
    provider_id    = request.args.get("providerDeviceId", type=str)

    page     = request.args.get("page", type=int)
    per_page = request.args.get("limit", type=int)

    prop = request.args.get("prop", type=str, default="id_nomenclature_device_type")
    dir = request.args.get("dir", type=str, default="asc")

    paginated = page is not None and per_page is not None

    schema = TrackingDevicesSchema(exclude=("deployments",), many=True)

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

    print(str(query))

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
    return TrackingDevicesSchema().dump(device)
