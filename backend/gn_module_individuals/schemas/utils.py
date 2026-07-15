from flask import current_app


def get_label(nomenclature):
    # Label in the configured language (DEFAULT_LANGUAGE), falling back to default.
    if nomenclature is None:
        return None
    lang = current_app.config.get("DEFAULT_LANGUAGE")
    label = getattr(nomenclature, f"label_{lang}", None)
    return label or nomenclature.label_default
