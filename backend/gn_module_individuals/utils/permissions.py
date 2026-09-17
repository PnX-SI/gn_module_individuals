from geonature.core.gn_permissions.tools import has_any_permissions

from .. import MODULE_CODE


def _has_ud(module_code):
    return has_any_permissions("U", module_code=module_code) and has_any_permissions(
        "D", module_code=module_code
    )


def can_link_module(module_code):
    """True if the current user may attach/detach an individual to/from module_code:
    flat U+D permission (no instance scope) on both INDIVIDUALS and module_code."""
    return _has_ud(MODULE_CODE) and _has_ud(module_code)
