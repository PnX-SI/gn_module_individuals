from marshmallow import fields

from geonature.core.gn_commons.schemas import ModuleSchema as CoreModuleSchema

from ..utils.permissions import can_link_module


class IndividualModuleSchema(CoreModuleSchema):
    """A module linked to an individual, with the current user's permission
    to attach/detach it."""

    can_unlink = fields.Method("get_can_unlink", dump_only=True)

    def get_can_unlink(self, obj):
        return can_link_module(obj.module_code)
