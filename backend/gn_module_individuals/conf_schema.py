"""
Spécification du schéma toml des paramètres de configurations
"""

from marshmallow import Schema, fields

class GnModuleSchemaConf(Schema):
  TEST_VAR = fields.String(load_default="Bonjour")