"""Add captures schemas

Revision ID: 0004
Revises: 0003_insert_nomenclatures
Create Date: 2026-08-03 15:09:10.810607

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import select, table, column, functions as func
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision = "0004_add_captures"
down_revision = "0003_insert_nomenclatures"
branch_labels = None
depends_on = None

SCHEMA_NAME = "gn_individual"


def upgrade():
    op.create_table(
        "t_captures",
        sa.Column(
            "id_capture",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "id_nomenclature_capture_protocol",
            sa.Integer(),
            sa.ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
            nullable=True,
        ),
        sa.Column(
            "comment",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "date",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "geom_local",
            Geometry("POINT"),
            nullable=False,
        ),
        sa.Column(
            "geom_4326",
            Geometry("POINT", 4326),
            nullable=False,
        ),
        sa.Column(
            "additional_data",
            postgresql.JSONB(),
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
        "t_individual_capture_observations",
        sa.Column(
            "id_capture",
            sa.Integer(),
            sa.ForeignKey(f"{SCHEMA_NAME}.t_captures.id_capture"),
            primary_key=True,
        ),
        sa.Column(
            "id_individual",
            sa.Integer(),
            sa.ForeignKey("gn_monitoring.t_individuals.id_individual"),
            primary_key=True,
        ),
        sa.Column(
            "additional_data",
            postgresql.JSONB(),
            nullable=True,
        ),
        schema=SCHEMA_NAME,
    )

    op.create_table(
        "cor_role_capture",
        sa.Column(
            "id_capture",
            sa.Integer(),
            sa.ForeignKey(f"{SCHEMA_NAME}.t_captures.id_capture"),
            primary_key=True,
        ),
        sa.Column(
            "id_role",
            sa.Integer(),
            sa.ForeignKey("utilisateurs.t_roles.id_role"),
            primary_key=True,
        ),
        schema=SCHEMA_NAME,
    )

    op.execute(f"""
        CREATE TRIGGER tr_meta_dates_captures
        BEFORE INSERT OR UPDATE ON {SCHEMA_NAME}.t_captures
        FOR EACH ROW
        EXECUTE FUNCTION {SCHEMA_NAME}.set_meta_dates();
    """)

    op.execute(f"""
        ALTER TABLE ONLY {SCHEMA_NAME}.t_individual_deployments
        ADD CONSTRAINT t_individual_deployments_id_capture_fkey
        FOREIGN KEY (id_capture) REFERENCES {SCHEMA_NAME}.t_captures (id_capture) NOT VALID;
    """)

    conn = op.get_bind()
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
                    "mnemonique": "PROTOCOLE_CAPTURE",
                    "label_default": "Protocole de capture",
                    "definition_default": "Méthode utilisée pour capturer les individus",
                    "label_fr": "Protocole de capture",
                    "definition_fr": "Méthode utilisée pour capturer les individus",
                    "source": "GEONATURE",
                },
            ]
        )
    )

    # Les nomenclatures créé ci-dessous ne sont que des nomenclatures de tests
    # Il faudrat ajouter des vrais nomenclatures

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
                    "cd_nomenclature": "1",
                    "mnemonique": "MAIN",
                    "label_default": "Capture à la main",
                    "definition_default": "Capture directe à la main",
                    "label_fr": "Capture à la main",
                    "definition_fr": "Capture directe à la main",
                    "source": "GEONATURE",
                    "hierarchy": "132.001",
                    "active": True,
                },
                {
                    "id_type": next_id,
                    "cd_nomenclature": "2",
                    "mnemonique": "FILET",
                    "label_default": "Filet",
                    "definition_default": "Capture au filet (épervier, filet japonais…)",
                    "label_fr": "Filet",
                    "definition_fr": "Capture au filet (épervier, filet japonais…)",
                    "source": "GEONATURE",
                    "hierarchy": "132.002",
                    "active": True,
                },
                {
                    "id_type": next_id,
                    "cd_nomenclature": "3",
                    "mnemonique": "PIEGE",
                    "label_default": "Piège",
                    "definition_default": "Capture au piège (cage, boîte, trappe…)",
                    "label_fr": "Piège",
                    "definition_fr": "Capture au piège (cage, boîte, trappe…)",
                    "source": "GEONATURE",
                    "hierarchy": "132.003",
                    "active": True,
                },
                {
                    "id_type": next_id,
                    "cd_nomenclature": "4",
                    "mnemonique": "TELEANESTHESIE",
                    "label_default": "Téléanesthésie",
                    "definition_default": "Capture par fléchette anesthésiante",
                    "label_fr": "Téléanesthésie",
                    "definition_fr": "Capture par fléchette anesthésiante",
                    "source": "GEONATURE",
                    "hierarchy": "132.004",
                    "active": True,
                },
            ]
        )
    )

    # Resync the sequence: the id_type above bypassed nextval().
    conn.execute(
        select(
            sa.func.setval(
                "ref_nomenclatures.bib_nomenclatures_types_id_type_seq",
                select(func.max(bib_nomencl.c.id_type)).scalar_subquery(),
            )
        )
    )

    op.execute(f"""
        ALTER TABLE ONLY {SCHEMA_NAME}.t_captures
        ADD CONSTRAINT check_t_captures_capture_protocol
        CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(id_nomenclature_capture_protocol, 'PROTOCOLE_CAPTURE'::character varying)) NOT VALID;
    """)


def downgrade():
    op.execute(f"""
        ALTER TABLE ONLY {SCHEMA_NAME}.t_captures
        DROP CONSTRAINT IF EXISTS check_t_captures_capture_protocol;
    """)

    op.execute("""
        DELETE FROM ref_nomenclatures.t_nomenclatures t
        USING ref_nomenclatures.bib_nomenclatures_types b
        WHERE t.id_type = b.id_type
        AND b.mnemonique = 'PROTOCOLE_CAPTURE';
    """)
    op.execute("""
        DELETE FROM ref_nomenclatures.bib_nomenclatures_types
        WHERE mnemonique = 'PROTOCOLE_CAPTURE';
    """)

    op.execute(f"""
        ALTER TABLE ONLY {SCHEMA_NAME}.t_individual_deployments
        DROP CONSTRAINT IF EXISTS t_individual_deployments_id_capture_fkey;
    """)

    op.execute(f"DROP TRIGGER IF EXISTS tr_meta_dates_captures ON {SCHEMA_NAME}.t_captures;")

    op.drop_table("cor_role_capture", schema=SCHEMA_NAME, if_exists=True)
    op.drop_table("t_individual_capture_observations", schema=SCHEMA_NAME, if_exists=True)
    op.drop_table("t_captures", schema=SCHEMA_NAME, if_exists=True)
