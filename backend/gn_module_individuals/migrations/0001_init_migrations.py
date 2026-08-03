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


def upgrade():
    conn = op.get_bind()
    op.execute(sa.text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}"))

    op.execute(sa.text("""
        INSERT INTO gn_permissions.t_objects (code_object, description_object)
        VALUES
            ('INDIVIDUALS_INDIVIDUALS', 'Gestion des individus'),
            ('INDIVIDUALS_SAMPLES',     'Gestion des échantillons dans Individus')
        ON CONFLICT (code_object) DO NOTHING
    """))

    op.execute(f"""
        INSERT INTO gn_permissions.t_permissions_available (
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
        FROM (
            VALUES
                ('{MODULE_CODE}', 'ALL',                    'R', True,  'Voir dans le module Individuals')
               ,('{MODULE_CODE}', 'INDIVIDUALS_INDIVIDUALS','C', True,  'Créer des individus')
               ,('{MODULE_CODE}', 'INDIVIDUALS_INDIVIDUALS','U', True,  'Éditer des individus')
               ,('{MODULE_CODE}', 'INDIVIDUALS_INDIVIDUALS','D', True,  'Supprimer des individus')
               ,('{MODULE_CODE}', 'INDIVIDUALS_SAMPLES',    'C', True,  'Créer des échantillons')
               ,('{MODULE_CODE}', 'INDIVIDUALS_SAMPLES',    'U', True,  'Éditer des échantillons')
               ,('{MODULE_CODE}', 'INDIVIDUALS_SAMPLES',    'D', True,  'Supprimer des échantillons')
        ) AS v (module_code, object_code, action_code, scope_filter, label)
        JOIN gn_commons.t_modules m     ON m.module_code  = v.module_code
        JOIN gn_permissions.t_objects o ON o.code_object  = v.object_code
        JOIN gn_permissions.bib_actions a ON a.code_action = v.action_code
    """)

    op.execute(f"""
        INSERT INTO gn_permissions.t_permissions (id_role, id_action, id_module, id_object, scope_value)
        SELECT
            r.id_role,
            a.id_action,
            m.id_module,
            o.id_object,
            NULL
        FROM (VALUES ('C'), ('U'), ('D')) AS v (action_code)
        JOIN utilisateurs.t_roles r      ON r.nom_role    = 'Grp_admin'
        JOIN gn_commons.t_modules m      ON m.module_code = '{MODULE_CODE}'
        JOIN gn_permissions.t_objects o  ON o.code_object = 'INDIVIDUALS_INDIVIDUALS'
        JOIN gn_permissions.bib_actions a ON a.code_action = v.action_code
        ON CONFLICT DO NOTHING
    """)


def downgrade():
    conn = op.get_bind()
    module_id = conn.execute(
        sa.text("""
            SELECT id_module FROM gn_commons.t_modules
            WHERE module_code = :module_code
        """),
        {"module_code": MODULE_CODE},
    ).scalar()

    conn.execute(
        sa.text("DELETE FROM gn_permissions.t_permissions_available WHERE id_module = :module_id"),
        {"module_id": module_id},
    )

    op.execute(sa.text("""
        DELETE FROM gn_permissions.t_permissions p
        USING utilisateurs.t_roles r,
              gn_permissions.t_objects o
        WHERE p.id_role   = r.id_role
          AND p.id_object = o.id_object
          AND r.nom_role    = 'Grp_admin'
          AND o.code_object = 'INDIVIDUALS_INDIVIDUALS'
    """))

    op.execute(sa.text("""
        DELETE FROM gn_permissions.t_objects
        WHERE code_object IN ('INDIVIDUALS_INDIVIDUALS', 'INDIVIDUALS_SAMPLES')
    """))

    op.execute(sa.text(f"DROP SCHEMA IF EXISTS {SCHEMA_NAME} CASCADE"))
