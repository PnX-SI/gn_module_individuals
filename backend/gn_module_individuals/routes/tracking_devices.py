from geonature.utils.json import pagination_schema, MyJSONProvider
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import joinedload

from flask import request, jsonify,g
from werkzeug.exceptions import NotFound, BadRequest

from geonature.core.gn_permissions import decorators as permissions
from geonature.core.gn_permissions.decorators import login_required
from geonature.utils.env import db
from utils_flask_sqla.response import json_resp

from .. import MODULE_CODE
from ..schemas import TrackingDevicesSchema
from ..models import TrackingDevices

from ..blueprint import blueprint

@blueprint.route("/devices", methods=["GET"])
@login_required
@permissions.check_cruved_scope("R", get_scope=True, module_code=MODULE_CODE)
@json_resp
def list_devices(scope):

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    schema = TrackingDevicesSchema(many=True)

    query = (
         db.select(TrackingDevices)
         .options(
             joinedload(TrackingDevices.nomenclature_device_type),
             joinedload(TrackingDevices.digitiser),
             joinedload(TrackingDevices.referer),
         )
    )
   
    pagination = db.paginate(query, page=page, per_page=per_page, error_out=False)
    return {
        "items": schema.dump(pagination.items),
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "prev_num": pagination.prev_num,
            "next_num": pagination.next_num,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        }
    }


@blueprint.route("/devices/<int(signed=True):id_tracking_device>", methods=["GET"])
@login_required
@permissions.check_cruved_scope("R", get_scope=True, module_code=MODULE_CODE)
@json_resp
def device(id_tracking_device, scope):
    query = (
        db.select(TrackingDevices)
        .options(
            joinedload(TrackingDevices.nomenclature_device_type),
            joinedload(TrackingDevices.digitiser),
            joinedload(TrackingDevices.referer),
        )
        .where(TrackingDevices.id_tracking_device == id_tracking_device)
    )

    device = db.session.execute(query).unique().scalar_one_or_none()

    if device is None:
        raise NotFound(f"Le matériel de suivi {id_tracking_device} n'a pas été trouvé")
    return TrackingDevicesSchema().dump(device)
   