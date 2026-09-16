"""Insert occtax individuals samples data for demo

Revision ID: 0004_additional_fields_samples
Revises:
Create Date: 2026-09-15 14:50:00

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0004_additional_fields_samples"
down_revision = "0003_monitoring_indiv_samples"


def upgrade():
    conn = op.get_bind()

    # Create a specific dataset waiting for the possibility to link additional fields to cd_nom
    op.execute(sa.text("""
        INSERT INTO gn_meta.t_datasets (
            id_acquisition_framework, dataset_name, dataset_shortname, dataset_desc,
            marine_domain, terrestrial_domain, id_digitizer
        )
        SELECT
            af.id_acquisition_framework, 'Gestion additional_data individus TEST', 'ADDITIONAL_DATA_INDIVIDUALS',
            'Jeu de données fictif de TEST pour la gestion des additional fields',
            FALSE, TRUE, 3
        FROM gn_meta.t_acquisition_frameworks af
        WHERE af.acquisition_framework_name = 'Cadre d''acquisition de test Individus'
    """))

    op.execute(sa.text("""
        INSERT INTO gn_commons.cor_module_dataset (id_module, id_dataset)
        SELECT m.id_module, d.id_dataset
        FROM gn_commons.t_modules m, gn_meta.t_datasets d
        WHERE m.module_code = 'INDIVIDUALS' AND d.dataset_shortname = 'ADDITIONAL_DATA_INDIVIDUALS'
    """))

    id_dataset = conn.execute(sa.text("""
        SELECT id_dataset 
        FROM gn_meta.t_datasets 
        WHERE dataset_shortname = 'ADDITIONAL_DATA_INDIVIDUALS'
    """)).scalar()

    id_module = conn.execute(sa.text("""
        SELECT id_module 
        FROM gn_commons.t_modules
        WHERE module_code = 'INDIVIDUALS'
    """)).scalar()

    id_object = conn.execute(sa.text("""
        SELECT id_object 
        FROM gn_permissions.t_objects
        WHERE code_object = 'INDIVIDUALS'
    """)).scalar()

    op.execute(sa.text("""
        INSERT INTO gn_commons.t_additional_fields
            (field_name,    field_label,            required,   description,                    id_widget,  quantitative,   unity,  additional_attributes,  code_nomenclature_type, field_values,   multiselect,    id_list,    api,    exportable, field_order, default_value)
        VALUES
            ('birth_year',  'Année de naissance',   false,      'Année estimée de naissance',   11,         false,          '',     '{}',                     '',                     '{}',             false,          0,          '',     true,       1,          ''),
            ('death_date',  'Date du décès',        false,      'Date du décès présumée',       9,          false,          '',     '{}',                     '',                     '{}',             false,          0,          '',     true,       2,          '');
    """))

    op.execute(sa.text("""
            INSERT INTO gn_commons.cor_field_dataset
                (id_field, id_dataset)
            SELECT id_field, :id_dataset
            FROM gn_commons.t_additional_fields
            WHERE field_name IN ('birth_year', 'death_date');
        """).bindparams(id_dataset=id_dataset))

    op.execute(sa.text("""
            INSERT INTO gn_commons.cor_field_module
                (id_field, id_module)
            SELECT id_field, :id_module
            FROM gn_commons.t_additional_fields
            WHERE field_name IN ('birth_year', 'death_date');
        """).bindparams(id_module=id_module))

    op.execute(sa.text("""
            INSERT INTO gn_commons.cor_field_object
                (id_field, id_object)
            SELECT id_field, :id_object
            FROM gn_commons.t_additional_fields
            WHERE field_name IN ('birth_year', 'death_date');
        """).bindparams(id_object=id_object))


def downgrade():
    op.execute(sa.text("""
       DELETE FROM gn_commons.t_additional_fields
       WHERE field_name IN ('birth_year', 'death_date');
    """))

    # cor_module_dataset is deleted in cascade with the dataset.
    op.execute(
        sa.text(
            "DELETE FROM gn_meta.t_datasets WHERE dataset_shortname = 'ADDITIONAL_DATA_INDIVIDUALS'"
        )
    )
