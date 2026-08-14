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
depends_on = "ad8b797d89c0"

MODULE_CODE = "INDIVIDUALS"
SCHEMA_NAME = "gn_individual"


def upgrade():
    conn = op.get_bind()
    op.execute(sa.text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME}"))

    op.execute(sa.text("""
        INSERT INTO gn_permissions.t_objects 
            (code_object, description_object)
        VALUES
            ('DEVICES', 'Gestion des devices'),
            ('SAMPLES', 'Gestion des échantillons')
        ON CONFLICT (code_object) DO NOTHING
        """))

    op.execute(
        sa.text(
            f"""
            INSERT INTO gn_permissions.cor_object_module (
                id_object,
                id_module
            )
            SELECT
                o.id_object,
                m.id_module
            FROM (
                VALUES
                    ('{MODULE_CODE}', 'INDIVIDUALS'),
                    ('{MODULE_CODE}', 'DEVICES'),
                    ('{MODULE_CODE}', 'SAMPLES')
            ) AS v (module_code, object_code)
            JOIN gn_commons.t_modules m
                ON m.module_code = v.module_code
            JOIN gn_permissions.t_objects o
                ON o.code_object = v.object_code;
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
                ('{MODULE_CODE}', 'INDIVIDUALS', 'R', True,  'Consulter le module Individuals')
                ,('{MODULE_CODE}', 'INDIVIDUALS','C', True,  'Créer des individus, des déploiements et des captures')
                ,('{MODULE_CODE}', 'INDIVIDUALS','U', True,  'Éditer des individus, des déploiements et des captures')
                ,('{MODULE_CODE}', 'INDIVIDUALS','D', True,  'Supprimer des individus, des déploiements et des captures')
                ,('{MODULE_CODE}', 'DEVICES','C', True,  'Créer des dispositifs de suivi')
                ,('{MODULE_CODE}', 'DEVICES','U', True,  'Éditer des dispositifs de suivi')
                ,('{MODULE_CODE}', 'DEVICES','D', True,  'Supprimer des dispositifs de suivi')
                ,('{MODULE_CODE}', 'SAMPLES',    'C', True,  'Créer des échantillons')
                ,('{MODULE_CODE}', 'SAMPLES',    'U', True,  'Éditer des échantillons')
                ,('{MODULE_CODE}', 'SAMPLES',    'D', True,  'Supprimer des échantillons')
        ) AS v (module_code, object_code, action_code, scope_filter, label)
        JOIN gn_commons.t_modules m     ON m.module_code  = v.module_code
        JOIN gn_permissions.t_objects o ON o.code_object  = v.object_code
        JOIN gn_permissions.bib_actions a ON a.code_action = v.action_code
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

    conn.execute(
        sa.text("""
            DELETE FROM gn_permissions.t_permissions p
            WHERE p.id_module = :module_id
            """),
        {"module_id": module_id},
    )

    op.execute(sa.text("""
            DELETE FROM gn_permissions.t_objects
            WHERE code_object IN ('DEVICES', 'SAMPLES')
            """))

    conn.execute(
        sa.text(
            """
                DELETE FROM gn_permissions.cor_object_module com
                WHERE com.id_module = :module_id
            """
        ),
        {"module_id": module_id},
    )

    op.execute(sa.text(f"DROP SCHEMA IF EXISTS {SCHEMA_NAME} CASCADE"))
