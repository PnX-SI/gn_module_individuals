"""Create tables

Revision ID: 0002_create_tables
Revises: 0001_init_migrations
Create Date: 2026-03-19 15:40:48.398854

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import select, table, column, functions as func

# revision identifiers, used by Alembic.
revision = "0002_create_tables"
down_revision = "0001_init_migrations"
branch_labels = None
depends_on = None

MODULE_CODE = "INDIVIDUALS"
SCHEMA_NAME = "gn_individual"


def upgrade():
    conn = op.get_bind()
    bib_tracking_devices = op.create_table(
        "bib_tracking_devices",
        sa.Column(
            "id_tracking_device",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "id_nomenclature_device_type",
            sa.Integer(),
            sa.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
            nullable=True,
        ),
        sa.Column(
            "provider_name",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "provider_device_id",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "id_referer",
            sa.Integer(),
            sa.ForeignKey("utilisateurs.t_roles.id_role"),
            nullable=True,
        ),
        sa.Column(
            "comment",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "id_digitiser",
            sa.Integer(),
            sa.ForeignKey("utilisateurs.t_roles.id_role"),
            nullable=True,
        ),
        sa.Column(
            "meta_create_date",
            sa.DateTime(),
            nullable=True,
        ),
        sa.Column(
            "meta_update_date",
            sa.DateTime(),
            nullable=True,
        ),
        schema=SCHEMA_NAME,
    )

    t_individual_deployments = op.create_table(
        "t_individual_deployments",
        sa.Column(
            "id_deployment",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "id_capture",
            sa.Integer(),
            # sa.ForeignKey("t_captures.id_capture"),
            nullable=False,
        ),
        sa.Column(
            "id_individual",
            sa.Integer(),
            sa.ForeignKey("gn_monitoring.t_individuals.id_individual"),
            nullable=False,
        ),
        sa.Column(
            "id_nomenclature_deployment_type",
            sa.Integer(),
            sa.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
            nullable=True,
        ),
        sa.Column(
            "id_nomenclature_deployment_location",
            sa.Integer(),
            sa.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
            nullable=True,
        ),
        sa.Column(
            "id_tracking_device",
            sa.Integer(),
            sa.ForeignKey("gn_individual.bib_tracking_devices.id_tracking_device"),
            nullable=False,
        ),
        sa.Column(
            "marking_code",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "install_date",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "removal_date",
            sa.DateTime(),
            nullable=True,
        ),
        sa.Column(
            "comment",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "id_digitiser",
            sa.Integer(),
            sa.ForeignKey("utilisateurs.t_roles.id_role"),
            nullable=True,
        ),
        sa.Column(
            "meta_create_date",
            sa.DateTime(),
            nullable=True,
        ),
        sa.Column(
            "meta_update_date",
            sa.DateTime(),
            nullable=True,
        ),
        schema=SCHEMA_NAME,
    )

    op.execute(f"""
        CREATE OR REPLACE FUNCTION {SCHEMA_NAME}.set_meta_dates()
        RETURNS TRIGGER AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                NEW.meta_create_date := NOW();
            ELSIF TG_OP = 'UPDATE' THEN
                NEW.meta_update_date := NOW();
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute(f"""
        CREATE TRIGGER tr_meta_dates_bib_tracking_devices
        BEFORE INSERT OR UPDATE ON {SCHEMA_NAME}.bib_tracking_devices
        FOR EACH ROW
        EXECUTE FUNCTION {SCHEMA_NAME}.set_meta_dates();
    """)

    op.execute(f"""
        CREATE TRIGGER tr_meta_dates_individual_deployments
        BEFORE INSERT OR UPDATE ON {SCHEMA_NAME}.t_individual_deployments
        FOR EACH ROW
        EXECUTE FUNCTION {SCHEMA_NAME}.set_meta_dates();
    """)

    bib_nomencl = table(
        "bib_nomenclatures_types",
        column("id_type", sa.Integer),
        column("mnemonique", sa.String),
        column("label_default", sa.String),
        column("definition_default", sa.String),
        column("label_fr", sa.String),
        column("definition_fr", sa.String),
        column("source", sa.String),
        schema="ref_nomenclatures",
    )

    req_obj = select(func.max(bib_nomencl.c.id_type))
    last_value = conn.execute(req_obj).scalar()
    next_id = (last_value or 0) + 1

    op.execute(
        sa.insert(bib_nomencl).values(
            [
                {
                    "id_type": next_id,
                    "mnemonique": "TYPE_DISPO_SUIVI",
                    "label_default": "Type de dispositif de suivi",
                    "definition_default": "Dispositif de suivi",
                    "label_fr": "Type de dispositif de suivi",
                    "definition_fr": "Dispositif de suivi",
                    "source": "GEONATURE",
                },
            ]
        )
    )

    t_nomencl = table(
        "t_nomenclatures",
        column("id_type", sa.Integer),
        column("cd_nomenclature", sa.String),
        column("mnemonique", sa.String),
        column("label_default", sa.String),
        column("definition_default", sa.String),
        column("label_fr", sa.String),
        column("definition_fr", sa.String),
        column("source", sa.String),
        column("hierarchy", sa.String),
        column("active", sa.Boolean),
        schema="ref_nomenclatures",
    )

    op.execute(
        sa.insert(t_nomencl).values(
            [
                {
                    "id_type": next_id,
                    "cd_nomenclature": 1,
                    "mnemonique": "GPS",
                    "label_default": "Balise GPS",
                    "definition_default": "Balise GPS",
                    "label_fr": "Balise GPS",
                    "definition_fr": "Balise GPS",
                    "source": "GEONATURE",
                    "hierarchy": "129.001",
                    "active": True,
                },
                {
                    "id_type": next_id,
                    "cd_nomenclature": 2,
                    "mnemonique": "GSM",
                    "label_default": "Balise GSM",
                    "definition_default": "Balise GSM",
                    "label_fr": "Balise GSM",
                    "definition_fr": "Balise GSM",
                    "source": "GEONATURE",
                    "hierarchy": "129.001",
                    "active": True,
                },
                {
                    "id_type": next_id,
                    "cd_nomenclature": 3,
                    "mnemonique": "Argos",
                    "label_default": "Balise Argos",
                    "definition_default": "Balise Argos",
                    "label_fr": "Balise Argos",
                    "definition_fr": "Balise Argos",
                    "source": "GEONATURE",
                    "hierarchy": "129.001",
                    "active": True,
                },
                {
                    "id_type": next_id,
                    "cd_nomenclature": 4,
                    "mnemonique": "VHF",
                    "label_default": "Balise VHF",
                    "definition_default": "Balise VHF",
                    "label_fr": "Balise VHF",
                    "definition_fr": "Balise VHF",
                    "source": "GEONATURE",
                    "hierarchy": "129.001",
                    "active": True,
                },
            ]
        )
    )


def downgrade():
    op.execute(
        f"DROP TRIGGER IF EXISTS tr_meta_dates_bib_tracking_devices ON {SCHEMA_NAME}.bib_tracking_devices;"
    )
    op.execute(
        f"DROP TRIGGER IF EXISTS tr_meta_dates_individual_deployments ON {SCHEMA_NAME}.t_individual_deployments;"
    )
    op.execute(f"DROP FUNCTION IF EXISTS {SCHEMA_NAME}.set_meta_dates();")
    op.drop_table("t_individual_deployments", schema=SCHEMA_NAME, if_exists=True)
    op.drop_table("bib_tracking_devices", schema=SCHEMA_NAME, if_exists=True)
    op.execute(f"""DELETE FROM ref_nomenclatures.t_nomenclatures t
            USING ref_nomenclatures.bib_nomenclatures_types b
            WHERE t.id_type = b.id_type
            AND b.mnemonique = 'TYPE_DISPO_SUIVI';
        """)
    op.execute(
        f"DELETE FROM ref_nomenclatures.bib_nomenclatures_types WHERE mnemonique = 'TYPE_DISPO_SUIVI';"
    )
