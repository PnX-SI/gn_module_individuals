from flask import make_response, request

from geonature.core.gn_commons.models import TModules
from geonature.core.gn_monitoring.models import TIndividuals
from geonature.core.gn_permissions import decorators as permissions
from geonature.core.gn_permissions.decorators import login_required
from geonature.utils.env import db
from utils_flask_sqla.response import json_resp

from .. import MODULE_CODE
from ..blueprint import blueprint
from ..schemas.modules import IndividualModuleSchema
from ..utils.errors import APIError, ApiErrorCode
from ..utils.permissions import can_link_module


def _get_individual_or_404(id_individual):
    individual = db.session.get(TIndividuals, id_individual)
    if individual is None:
        raise APIError(
            ApiErrorCode.NOT_FOUND,
            f"Individual with id {id_individual} was not found.",
            404,
            params={"id": id_individual},
        )
    return individual


@blueprint.route("/individuals/<int(signed=True):id_individual>/modules", methods=["GET"])
@login_required
@permissions.check_cruved_scope(
    "R", get_scope=True, module_code=MODULE_CODE, object_code="INDIVIDUALS"
)
@json_resp
def list_individual_modules(id_individual, scope):
    """
    List the modules linked to one individual

    .. :quickref: Individuals;

    :param id_individual: the id_individual
    :type id_individual: int

    :returns: the linked modules, each with a ``can_unlink`` flag for the
        current user
    :rtype: list<TModules>
    """
    individual = _get_individual_or_404(id_individual)
    if not individual.has_instance_permission(scope):
        raise APIError(
            ApiErrorCode.INSUFFICIENT_PERMISSIONS,
            f"You do not have permission to read individual {id_individual}.",
            403,
        )
    return IndividualModuleSchema(many=True).dump(individual.modules)


@blueprint.route("/individuals/<int(signed=True):id_individual>/modules", methods=["POST"])
@login_required
@json_resp
def link_individual_module(id_individual):
    """
    Link one individual to a module

    .. :quickref: Individuals;

    Linking (and unlinking, see :func:`unlink_individual_module`) an
    individual to a module requires the current user to have, regardless of
    instance scope, both U and D permission on the target module and on
    INDIVIDUALS (see :func:`..utils.permissions.can_link_module`).

    Expects a JSON body ``{"id_module": <int>}``.

    :param id_individual: the id_individual
    :type id_individual: int

    :returns: the linked module
    :rtype: dict<TModules>
    """
    individual = _get_individual_or_404(id_individual)

    data = request.get_json(silent=True)
    id_module = data.get("id_module") if data else None
    if not isinstance(id_module, int):
        raise APIError(
            ApiErrorCode.VALIDATION_ERROR,
            "id_module is required and must be an integer.",
            400,
        )

    module = db.session.get(TModules, id_module)
    if module is None:
        raise APIError(
            ApiErrorCode.NOT_FOUND,
            f"Module with id {id_module} was not found.",
            404,
            params={"id": id_module},
        )

    if not can_link_module(module.module_code):
        raise APIError(
            ApiErrorCode.INSUFFICIENT_PERMISSIONS,
            f"You do not have permission to link individual {id_individual} to module "
            f"{module.module_code}.",
            403,
        )

    if module in individual.modules:
        raise APIError(
            ApiErrorCode.ALREADY_LINKED,
            f"Individual {id_individual} is already linked to module {module.module_code}.",
            409,
            params={"id": id_individual, "id_module": id_module},
        )

    individual.modules.append(module)
    db.session.commit()

    return IndividualModuleSchema().dump(module), 201


@blueprint.route(
    "/individuals/<int(signed=True):id_individual>/modules/<int(signed=True):id_module>",
    methods=["DELETE"],
)
@login_required
def unlink_individual_module(id_individual, id_module):
    """
    Unlink one individual from a module

    .. :quickref: Individuals;

    See :func:`link_individual_module` for the permission rule.

    :param id_individual: the id_individual
    :type id_individual: int
    :param id_module: the id_module
    :type id_module: int

    :returns: empty response
    """
    individual = _get_individual_or_404(id_individual)

    module = db.session.get(TModules, id_module)
    if module is None or module not in individual.modules:
        raise APIError(
            ApiErrorCode.NOT_FOUND,
            f"Individual {id_individual} is not linked to module {id_module}.",
            404,
            params={"id": id_individual, "id_module": id_module},
        )

    if not can_link_module(module.module_code):
        raise APIError(
            ApiErrorCode.INSUFFICIENT_PERMISSIONS,
            f"You do not have permission to unlink individual {id_individual} from module "
            f"{module.module_code}.",
            403,
        )

    individual.modules.remove(module)
    db.session.commit()

    return make_response("", 204)
