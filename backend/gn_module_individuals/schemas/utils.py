from flask import current_app


def get_label(nomenclature):
    # Label in the configured language (DEFAULT_LANGUAGE), falling back to default.
    if nomenclature is None:
        return None
    lang = current_app.config.get("DEFAULT_LANGUAGE")
    label = getattr(nomenclature, f"label_{lang}", None)
    return label or nomenclature.label_default


def is_nomenclature_of_type(nomenclature, mnemonique):
    """Whether a TNomenclatures instance belongs to the given type (by mnemonique)."""
    return nomenclature is not None and nomenclature.nomenclature_type.mnemonique == mnemonique
