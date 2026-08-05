"""Create tables

Revision ID: 0002_create_tables
Revises: 0001_init_migrations
Create Date: 2026-03-19 15:40:48.398854

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_create_tables"
down_revision = "0001_init_migrations"
branch_labels = None
depends_on = None

MODULE_CODE = "INDIVIDUALS"
SCHEMA_NAME = "gn_individual"


def upgrade():
    op.create_table(
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

    op.create_table(
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
            nullable=False,
        ),
        sa.Column(
            "id_nomenclature_deployment_location",
            sa.Integer(),
            sa.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
            nullable=False,
        ),
        sa.Column(
            "id_tracking_device",
            sa.Integer(),
            sa.ForeignKey("gn_individual.bib_tracking_devices.id_tracking_device"),
            nullable=True,
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
        sa.Column("meta_create_date", sa.DateTime(), nullable=True, server_default=sa.func.now()),
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
            IF TG_OP = 'UPDATE' THEN
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

    op.execute(f"""
        ALTER TABLE ONLY {SCHEMA_NAME}.bib_tracking_devices
        ADD CONSTRAINT check_bib_tracking_devices_device_type
        CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_device_type, 'TYPE_DISPO_SUIVI'::character varying)) NOT VALID;
    """)

    op.execute(f"""
        ALTER TABLE ONLY {SCHEMA_NAME}.t_individual_deployments
        ADD CONSTRAINT check_t_individual_deployments_deployment_type
        CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_deployment_type, 'TYPE_MARQUAGE'::character varying)) NOT VALID;
    """)

    op.execute(f"""
        ALTER TABLE ONLY {SCHEMA_NAME}.t_individual_deployments
        ADD CONSTRAINT check_t_individual_deployments_deployment_location
        CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_deployment_location, 'LOC_MARQUAGE'::character varying)) NOT VALID;
    """)


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
