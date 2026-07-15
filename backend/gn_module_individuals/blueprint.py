"""Individuals module blueprint: registers routes and error handling."""

from flask import Blueprint

blueprint = Blueprint("individuals", __name__, cli_group="individuals")

from .utils.errors import APIError, handle_error  # noqa: F401

blueprint.register_error_handler(APIError, handle_error)

from .routes import individuals, observations, captures, devices  # noqa: F401
