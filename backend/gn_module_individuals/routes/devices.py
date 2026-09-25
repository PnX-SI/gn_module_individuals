import json

from flask import request, jsonify, g, make_response
from marshmallow import EXCLUDE, ValidationError

from sqlalchemy import func
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.exc import IntegrityError

from geonature.core.gn_permissions import decorators as permissions
from geonature.core.gn_permissions.decorators import login_required
from geonature.core.gn_monitoring.models import TIndividuals
from geonature.utils.env import db
from utils_flask_sqla.response import json_resp, to_csv_resp

from pypnnomenclature.models import TNomenclatures
from pypnnomenclature.schemas import NomenclatureSchema
from pypnusershub.db.models import User
from ..utils.errors import APIError, ApiErrorCode

from .. import MODULE_CODE
from ..schemas import (
    TrackingDeviceDetailSchema,
    TrackingDeviceListSchema,
    TrackingDeviceWriteSchema,
)
from ..models import TrackingDevices, IndividualDeployments

from ..blueprint import blueprint
from .utils import check_export_format, export_filename


def _parse_bool(value):
    if value is None or value == "":
        return None
    normalized = value.lower()
    if normalized in ("true", "1", "yes", "y"):
        return True
    if normalized in ("false", "0", "no", "n"):
        return False
    raise APIError(ApiErrorCode.INVALID_FILTER, "Unsupported available value", 400)


def _device_available_expression():
    """A device is available when it has 0 deployment, or when its last
    deployment has a  removal_date."""
    has_deployment = (
        db.select(IndividualDeployments.id_deployment)
        .where(IndividualDeployments.id_tracking_device == TrackingDevices.id_tracking_device)
        .correlate(TrackingDevices)
        .exists()
    )
    last_removal_date = (
        db.select(IndividualDeployments.removal_date)
        .where(IndividualDeployments.id_tracking_device == TrackingDevices.id_tracking_device)
        .order_by(IndividualDeployments.install_date.desc())
        .limit(1)
        .correlate(TrackingDevices)
        .scalar_subquery()
    )
    return db.or_(~has_deployment, last_removal_date.isnot(None))


@blueprint.route("/devices/<int(signed=True):id_tracking_device>", methods=["GET"])
@login_required
@permissions.check_cruved_scope(
    "R", get_scope=True, module_code=MODULE_CODE, object_code="INDIVIDUALS"
)
@json_resp
def device(id_tracking_device, scope):
    """
    Return one tracking device

    .. :quickref: Devices;

    :param id_tracking_device: the id_tracking_device
    :type id_tracking_device: int

    :returns: a dict representing one tracking device with its nomenclatures,
        referer, digitiser and deployments
    :rtype: dict<TrackingDevices>
    """
    # Detail schema always exposes every relationship of the model.
    relationship_fields = list(TrackingDevices.__nomenclatures__) + ["referer", "digitiser"]
    schema = TrackingDeviceDetailSchema(only=["+cruved"] + relationship_fields)

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
            ApiErrorCode.NOT_FOUND,
            f"Tracking device with id {id_tracking_device} was not found.",
            404,
        )
    if not device.has_instance_permission(scope):
        raise APIError(
            ApiErrorCode.INSUFFICIENT_PERMISSIONS,
            f"You do not have permission to read this device.",
            403,
        )
    return schema.dump(device)


def _parse_device_filters(args):
    return {
        "cd_nom": args.get("cd_nom", type=int),
        "device_type": args.get("id_nomenclature_device_type", type=int),
        "provider_name": args.get("provider_name", type=str),
        "search": args.get("search", type=str),
        "id_referer": args.get("id_referer", type=int),
        "available": _parse_bool(args.get("available")),
    }


_DEVICE_VIRTUAL_SORT_COLS = {
    "referer_name": (
        db.select(func.concat(User.prenom_role, " ", User.nom_role))
        .where(User.id_role == TrackingDevices.id_referer)
        .correlate(TrackingDevices)
        .scalar_subquery()
    ),
    "nomenclature_device_type_name": (
        db.select(TNomenclatures.label_default)
        .where(TNomenclatures.id_nomenclature == TrackingDevices.id_nomenclature_device_type)
        .correlate(TrackingDevices)
        .scalar_subquery()
    ),
    "last_individual_equipped_name": (
        db.select(TIndividuals.individual_name)
        .join(
            IndividualDeployments,
            IndividualDeployments.id_individual == TIndividuals.id_individual,
        )
        .where(IndividualDeployments.id_tracking_device == TrackingDevices.id_tracking_device)
        .order_by(IndividualDeployments.install_date.desc())
        .limit(1)
        .correlate(TrackingDevices)
        .scalar_subquery()
    ),
}


def _build_devices_query(scope, filters, *, prop="meta_create_date", dir="desc", eager_load=True):
    sort_col = _DEVICE_VIRTUAL_SORT_COLS.get(prop)
    if sort_col is None:
        sort_col = getattr(TrackingDevices, prop, None)
    if sort_col is None:
        sort_col = TrackingDevices.meta_create_date

    query = db.select(TrackingDevices)
    if eager_load:
        query = query.options(
            joinedload(TrackingDevices.nomenclature_device_type),
            selectinload(TrackingDevices.digitiser),
            selectinload(TrackingDevices.referer),
            joinedload(TrackingDevices.deployments).joinedload(IndividualDeployments.individual),
        )
    # Requested sort, then id_tracking_device desc as a mandatory tie-breaker
    # (same convention as occtax.repositories) for stable pagination when
    # the sort column has ties.
    query = query.order_by(
        sort_col.desc() if dir == "desc" else sort_col.asc(),
        TrackingDevices.id_tracking_device.desc(),
    )

    if filters["device_type"] is not None:
        query = query.where(TrackingDevices.id_nomenclature_device_type == filters["device_type"])
    if filters["provider_name"]:
        query = query.where(TrackingDevices.provider_name.ilike(f"%{filters['provider_name']}%"))
    if filters["search"]:
        query = query.where(TrackingDevices.device_label.ilike(f"%{filters['search']}%"))
    if filters["id_referer"] is not None:
        query = query.where(TrackingDevices.id_referer == filters["id_referer"])
    if filters["available"] is not None:
        available_expr = _device_available_expression()
        query = query.where(available_expr if filters["available"] else ~available_expr)
    if filters["cd_nom"] is not None:
        query = query.where(
            db.select(IndividualDeployments.id_deployment)
            .join(TIndividuals, TIndividuals.id_individual == IndividualDeployments.id_individual)
            .where(
                IndividualDeployments.id_tracking_device == TrackingDevices.id_tracking_device,
                TIndividuals.cd_nom == filters["cd_nom"],
            )
            .exists()
        )

    return TrackingDevices.filter_by_scope(query, scope)


@blueprint.route("/devices", methods=["GET"])
@login_required
@permissions.check_cruved_scope(
    "R", get_scope=True, module_code=MODULE_CODE, object_code="INDIVIDUALS"
)
@json_resp
def list_devices(scope):
    """
    List tracking devices

    .. :quickref: Devices;

    :query int cd_nom: filter on the cd_nom of the last individual equipped
        with the device
    :query int id_nomenclature_device_type: filter on the device type
    :query string provider_name: filter on the provider name (partial match)
    :query string search: filter on the device label (``provider_name-
       provider_device_id``), partial match, for autocomplete
    :query int id_referer: filter on the referer role
    :query boolean available: filter on device availability
    :query int page: page number, requires per_page to enable pagination
    :query int per_page: page size, requires page to enable pagination
    :query string prop: column to sort on (default: meta_create_date)
    :query string dir: sort direction, ``asc`` or ``desc`` (default: desc)

    :returns: `list<TrackingDevices>`, wrapped in a pagination envelope
        (``items``, ``total``, ``pages``, ``has_next``...) when page and
        per_page are provided
    :rtype: dict|list
    """
    filters = _parse_device_filters(request.args)

    page = request.args.get("page", type=int)
    per_page = request.args.get("per_page", type=int)

    prop = request.args.get("prop", type=str, default="meta_create_date")
    dir = request.args.get("dir", type=str, default="desc")

    paginated = page is not None and per_page is not None

    schema = TrackingDeviceListSchema(only=["+cruved"])

    query = _build_devices_query(scope, filters, prop=prop, dir=dir)

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
    "C", get_scope=True, module_code=MODULE_CODE, object_code="INDIVIDUALS"
)
@json_resp
def create_device(scope):
    """
    Post one new tracking device

    .. :quickref: Devices;

    Expects a JSON body matching ``TrackingDeviceWriteSchema``.

    :returns: the created device
    :rtype: dict<TrackingDevices>
    """
    data = request.get_json(silent=True)

    if not data:
        raise APIError(
            ApiErrorCode.MISSING_JSON_BODY,
            "Missing JSON request body.",
            400,
        )

    schema = TrackingDeviceWriteSchema(unknown=EXCLUDE)
    try:
        device = schema.load(data)
    except ValidationError as e:
        raise APIError(
            ApiErrorCode.VALIDATION_ERROR,
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
    "U", get_scope=True, module_code=MODULE_CODE, object_code="INDIVIDUALS"
)
@json_resp
def update_device(id_tracking_device, scope):
    """
    Update one tracking device

    .. :quickref: Devices;

    Expects a JSON body matching ``TrackingDeviceWriteSchema``.

    :param id_tracking_device: the id_tracking_device
    :type id_tracking_device: int

    :returns: the updated device
    :rtype: dict<TrackingDevices>
    """
    device = db.session.get(TrackingDevices, id_tracking_device)
    if device is None:
        raise APIError(
            ApiErrorCode.NOT_FOUND,
            f"Tracking device with id {id_tracking_device} was not found.",
            404,
        )
    data = request.get_json(silent=True)

    if not data:
        raise APIError(
            ApiErrorCode.MISSING_JSON_BODY,
            "Missing JSON request body.",
            400,
        )
    if not device.has_instance_permission(scope):
        raise APIError(
            ApiErrorCode.INSUFFICIENT_PERMISSIONS,
            f"You do not have permission to update device {id_tracking_device}.",
            403,
        )

    schema = TrackingDeviceWriteSchema(unknown=EXCLUDE)
    try:
        device = schema.load(data, instance=device)
    except ValidationError as e:
        raise APIError(
            ApiErrorCode.VALIDATION_ERROR,
            f"Validation failed: {json.dumps(e.messages)}",
            400,
        )

    device.id_digitiser = g.current_user.id_role

    db.session.commit()

    return schema.dump(device), 200


@blueprint.route("/devices/<int(signed=True):id_tracking_device>", methods=["DELETE"])
@login_required
@permissions.check_cruved_scope(
    "D", get_scope=True, module_code=MODULE_CODE, object_code="INDIVIDUALS"
)
def delete_device(id_tracking_device, scope):
    """
    Delete one tracking device

    .. :quickref: Devices;

    :param id_tracking_device: the id_tracking_device
    :type id_tracking_device: int

    :returns: empty response
    """
    device = db.session.get(TrackingDevices, id_tracking_device)
    if device is None:
        raise APIError(
            ApiErrorCode.NOT_FOUND,
            f"Tracking device with id {id_tracking_device} was not found.",
            404,
        )

    if not device.has_instance_permission(scope):
        raise APIError(
            ApiErrorCode.INSUFFICIENT_PERMISSIONS,
            f"You do not have permission to delete device {id_tracking_device}.",
            403,
        )

    deployment_count = db.session.scalar(
        db.select(func.count())
        .select_from(IndividualDeployments)
        .where(IndividualDeployments.id_tracking_device == id_tracking_device)
    )
    if deployment_count:
        raise APIError(
            ApiErrorCode.HAS_DEPLOYMENT,
            "This device cannot be deleted because it is associated with deployments.",
            409,
            params={"id": id_tracking_device, "nb": deployment_count},
        )

    db.session.delete(device)
    db.session.commit()
    return make_response("", 204)


@blueprint.route("/devices/export/<export_format>", methods=["POST"])
@login_required
# See export_individuals() in routes/individuals.py: "R" until "E"
# is configured.
@permissions.check_cruved_scope(
    "R", get_scope=True, module_code=MODULE_CODE, object_code="INDIVIDUALS"
)
# @permissions.check_cruved_scope(
#     "E", get_scope=True, module_code=MODULE_CODE, object_code="INDIVIDUALS"
# )
def export_devices(export_format, scope):
    """
    Export the currently filtered devices list

    .. :quickref: Devices;

    The route is in POST to accept the same filters as GET /devices without
    an overly long query string. Exports the whole filtered/sorted/scoped
    list (not a selection of checked rows), bounded by DEVICES.NB_MAX_EXPORT.

    :param export_format: ``csv`` (see the DEVICES.EXPORT_FORMAT module config)
    :type export_format: str

    :returns: a file attachment
    """
    entity_config = blueprint.config["DEVICES"]
    check_export_format(export_format, entity_config)

    filters = _parse_device_filters(request.args)
    # eager_load=True (the default): TrackingDeviceListSchema reads the same
    # nomenclature_device_type/digitiser/referer/deployments relationships as
    # list_devices().
    query = _build_devices_query(scope, filters).limit(entity_config["NB_MAX_EXPORT"])

    devices = db.session.scalars(query).unique().all()

    columns = entity_config["EXPORT_COLUMNS"] or None
    schema = TrackingDeviceListSchema(only=columns)
    return to_csv_resp(
        export_filename("devices"),
        schema.dump(devices, many=True),
        columns=list(schema.dump_fields.keys()),
        separator=";",
    )
