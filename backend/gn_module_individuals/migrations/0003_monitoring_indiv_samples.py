"""Insert monitoring individuals samples data for demo only if submodule cmr_bouquetins is installed

Revision ID: 0003_monitoring_indiv_samples
Revises:
Create Date: 2026-03-19 16:53:24.982945

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0003_monitoring_indiv_samples"
down_revision = "0002_occtax_indiv_samples"


def upgrade():
    conn = op.get_bind()

    # --- Monitoring integration: CMR_BOUQUETIN sub-module on our marked ibex ---
    # The sub-module must have been installed beforehand via
    # ./scripts/setup_cmr_demo.sh (see that script for details).
    cmr_installed = conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM gn_commons.t_modules WHERE module_code = 'CMR_BOUQUETIN')"
        )
    ).scalar()

    if cmr_installed:
        # Dedicated dataset: the dataset "1" reused for Occtax is associated
        # (gn_commons.cor_module_dataset) with the OCCTAX module only, not CMR_BOUQUETIN.
        op.execute(sa.text("""
            INSERT INTO gn_meta.t_datasets (
                id_acquisition_framework, dataset_name, dataset_shortname, dataset_desc,
                marine_domain, terrestrial_domain, id_digitizer
            )
            SELECT
                af.id_acquisition_framework, 'Suivi CMR bouquetins TEST', 'CMR_BOUQUETIN',
                'Jeu de données du suivi capture-marquage-recapture des bouquetins du Parc national de la Vanoise',
                FALSE, TRUE, 4
            FROM gn_meta.t_acquisition_frameworks af
            WHERE af.acquisition_framework_name = 'Cadre d''acquisition de test Individus'
        """))

        op.execute(sa.text("""
            INSERT INTO gn_commons.cor_module_dataset (id_module, id_dataset)
            SELECT m.id_module, d.id_dataset
            FROM gn_commons.t_modules m, gn_meta.t_datasets d
            WHERE m.module_code = 'CMR_BOUQUETIN' AND d.dataset_shortname = 'CMR_BOUQUETIN'
        """))

        op.execute(sa.text("""
            WITH site_data (base_site_name, lon, lat, id_digitiser) AS (
                VALUES
                ('Pointe de la Réchasse', 6.9100, 45.4050, 4),
                ('Plan du Lac',           6.9050, 45.3160, 6),
                ('Refuge de l''Arpont',   6.8541, 45.3350, 6),
                ('Col d''Aussois',        6.9917, 45.2394, 3)
            )
            INSERT INTO gn_monitoring.t_base_sites (base_site_name, id_digitiser, id_inventor, geom)
            SELECT d.base_site_name, d.id_digitiser, d.id_digitiser,
                ST_SetSRID(ST_MakePoint(d.lon, d.lat), 4326)
            FROM site_data d
        """))

        op.execute(sa.text("""
            WITH visit_data (base_site_name, visit_date, id_digitiser) AS (
                VALUES
                ('Pointe de la Réchasse', '2026-07-03'::date, 4),
                ('Plan du Lac',           '2026-07-06'::date, 6),
                ('Refuge de l''Arpont',   '2026-07-11'::date, 6),
                ('Col d''Aussois',        '2026-07-16'::date, 3)
            ),
            cmr_module AS (
                SELECT id_module FROM gn_commons.t_modules WHERE module_code = 'CMR_BOUQUETIN'
            ),
            cmr_dataset AS (
                SELECT id_dataset FROM gn_meta.t_datasets WHERE dataset_shortname = 'CMR_BOUQUETIN'
            )
            INSERT INTO gn_monitoring.t_base_visits (
                id_base_site, id_dataset, id_module, id_digitiser, visit_date_min
            )
            SELECT s.id_base_site, ds.id_dataset, m.id_module, v.id_digitiser, v.visit_date
            FROM visit_data v
            JOIN gn_monitoring.t_base_sites s ON s.base_site_name = v.base_site_name
            CROSS JOIN cmr_module m
            CROSS JOIN cmr_dataset ds
        """))

        op.execute(sa.text("""
            INSERT INTO gn_monitoring.cor_visit_observer (id_base_visit, id_role)
            SELECT bv.id_base_visit, bv.id_digitiser
            FROM gn_monitoring.t_base_visits bv
            JOIN gn_monitoring.t_base_sites s ON s.id_base_site = bv.id_base_site
            WHERE s.base_site_name IN (
                'Pointe de la Réchasse', 'Plan du Lac', 'Refuge de l''Arpont', 'Col d''Aussois'
            )
        """))

        op.execute(sa.text("""
            WITH obs_data (base_site_name, individual_name, id_digitiser) AS (
                VALUES
                ('Pointe de la Réchasse', 'Obiwan',     4),
                ('Plan du Lac',           'Evasion',    6),
                ('Refuge de l''Arpont',   'Tempête',    6),
                ('Col d''Aussois',        'Patastrophe',3)
            )
            INSERT INTO gn_monitoring.t_observations (id_base_visit, id_digitiser, id_individual)
            SELECT bv.id_base_visit, o.id_digitiser, i.id_individual
            FROM obs_data o
            JOIN gn_monitoring.t_base_sites s ON s.base_site_name = o.base_site_name
            JOIN gn_monitoring.t_base_visits bv ON bv.id_base_site = s.id_base_site
            JOIN gn_monitoring.t_individuals i ON i.individual_name = o.individual_name
        """))


def downgrade():
    conn = op.get_bind()

    dataset = conn.execute(
        sa.text(
            "SELECT id_dataset FROM gn_meta.t_datasets WHERE dataset_shortname = 'CMR_BOUQUETIN'"
        )
    ).scalar()

    # DELETEs (ON DELETE CASCADE) to
    # visits/observations and occurrences/counts, including synthese
    # (synthese deletion triggers on occtax and monitoring).
    if conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM gn_commons.t_modules WHERE module_code = 'CMR_BOUQUETIN')"
        )
    ).scalar():
        op.execute(sa.text("""
                DELETE FROM gn_monitoring.t_base_sites
                WHERE base_site_name IN (
                    'Pointe de la Réchasse', 'Plan du Lac', 'Refuge de l''Arpont', 'Col d''Aussois'
                )
                """))

        # cor_module_dataset is deleted in cascade with the dataset.
        op.execute(
            sa.text("DELETE FROM gn_meta.t_datasets WHERE dataset_shortname = 'CMR_BOUQUETIN'")
        )

    op.execute(sa.text("""
            DELETE FROM gn_monitoring.t_base_visits
            WHERE id_dataset = :dataset
            """).bindparams(dataset=dataset))
