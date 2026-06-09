"""init model

Revision ID: 0001_init_migrations
Revises:
Create Date: 2023-03-27 11:54:34.602380

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_init_migrations"
down_revision = None
branch_labels = ("individuals",)
depends_on = None

MODULE_CODE = "INDIVIDUALS"
SCHEMA_NAME = "gn_individual"
# TABLE_NAME = "t_individuals"
# PRIMARY_KEY = "id_demo"


def upgrade():
    # #########################################################################
    # Schema pr_demo
    # #########################################################################
    conn = op.get_bind()
    op.execute(sa.text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}"))

    ## ########################################################################
    ## Module permissions
    ## ########################################################################
    op.execute(f"""
      INSERT INTO
          gn_permissions.t_permissions_available (
              id_module,
              id_object,
              id_action,
              label,
              scope_filter
          )
      SELECT
          m.id_module,
          o.id_object,
          a.id_action,
          v.label,
          v.scope_filter
      FROM
          (
              VALUES
                  ('{MODULE_CODE}', 'ALL', 'C', False, 'Créer dans le module Individuals')
                  ,('{MODULE_CODE}', 'ALL', 'R', True, 'Voir dans le module Individuals')
                  ,('{MODULE_CODE}', 'ALL', 'U', True, 'Modifier dans le module Individuals')
                  ,('{MODULE_CODE}', 'ALL', 'V', True, 'Valider dans le module Individuals')
                  ,('{MODULE_CODE}', 'ALL', 'D', True, 'Supprimer dans le module Individuals')
          ) AS v (module_code, object_code, action_code, scope_filter, label)
      JOIN
          gn_commons.t_modules m ON m.module_code = v.module_code
      JOIN
          gn_permissions.t_objects o ON o.code_object = v.object_code
      JOIN
          gn_permissions.bib_actions a ON a.code_action = v.action_code
      """)


def downgrade():
    conn = op.get_bind()
    module_id = conn.execute(
        sa.text("""
            SELECT id_module
            FROM gn_commons.t_modules
            WHERE module_code = :module_code
            """),
        {"module_code": MODULE_CODE},
    ).scalar()

    conn.execute(
        sa.text("""
            DELETE FROM gn_permissions.t_permissions_available
            WHERE id_module = :module_id
            """),
        {"module_id": module_id},
    )

    op.execute(sa.text(f"DROP SCHEMA IF EXISTS {SCHEMA_NAME} CASCADE"))
