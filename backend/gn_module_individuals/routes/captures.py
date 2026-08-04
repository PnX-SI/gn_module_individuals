from geonature.utils.json import pagination_schema, MyJSONProvider
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import joinedload

from flask import request, jsonify, g
from werkzeug.exceptions import Forbidden, NotFound, BadRequest

from geonature.core.gn_permissions import decorators as permissions
from geonature.core.gn_permissions.decorators import login_required
from geonature.utils.env import db
from utils_flask_sqla.response import json_resp
from marshmallow import EXCLUDE, fields,Schema

from gn_module_individuals import MODULE_CODE
from gn_module_individuals.models.captures import Capture

from ..blueprint import blueprint


@blueprint.route("/captures", methods=["GET"])
@permissions.check_cruved_scope(
    "R", get_scope=True, module_code=MODULE_CODE, object_code="INDIVIDUALS"
)
@login_required
def list_captures(scope):
    return {}


@blueprint.route("/captures/<int(signed):id_capture>", methods=["DELETE"])
@login_required
@permissions.check_cruved_scope(
    "D", get_scope=True, module_code=MODULE_CODE, object_code="INDIVIDUALS"
)
def delete_capture(scope,id_capture):
    cap = db.session.get(Capture,id_capture)
    if cap.has_instance_permission(scope):
      db.session.delete(cap)
      db.session.commit()
    return True, 204

@blueprint.route("/captures/<int(signed):id_capture>", methods=["GET"])
@login_required
@permissions.check_cruved_scope(
    "R", get_scope=True, module_code=MODULE_CODE, object_code="INDIVIDUALS"
)
def get_capture_by_id(scope,id_capture):
    cap = db.session.get(Capture,id_capture)
    if not cap.has_instance_permission():
      raise Forbidden()

    serialized_cap = Schema().dump(cap)
    return serialized_cap,200


@blueprint.route("/captures", methods=["POST"])
@login_required
@permissions.check_cruved_scope(
    "C", get_scope=True, module_code=MODULE_CODE, object_code="INDIVIDUALS"
)
def post_capture():
    schema = Schema()
    post_data = request.get_json(silent=True)
    if not "id_digitiser" in post_data:
       post_data["id_digitiser"] = g.current_user.id_role
    capture = schema.load(post_data,unknown=EXCLUDE)
    db.sesion.add(capture)
    db.session.commit()
    return schema.dump(capture),204


@blueprint.route("/captures/<int(signed):id_capture>", methods=["POST"])
@login_required
@permissions.check_cruved_scope(
    "U", get_scope=True, module_code=MODULE_CODE, object_code="INDIVIDUALS"
)
def patch_capture(scope,id_capture):
    post_data = request.get_json(silent=True)
    if not "id_capture" in post_data:
       post_data["id_capture"] = id_capture
    capture= db.session.get(Capture,id_capture)
    if not capture.has_instance_permissions(scope):
       raise Forbidden(f"The user cannot modify this capture ! ")
    capture_ma = Schema().load(post_data)
    db.session.add(capture_ma)
    db.session.commit()
    return Schema().dump(capture_ma)


