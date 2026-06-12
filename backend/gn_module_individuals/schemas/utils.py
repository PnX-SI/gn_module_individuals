from flask import current_app


def get_label(nomenclature):
    #  Retourne le label dans la langue configurée (DEFAULT_LANGUAGE), avec fallback.
    if nomenclature is None:
        return None
    lang = current_app.config.get("DEFAULT_LANGUAGE")
    label = getattr(nomenclature, f"label_{lang}", None)
    return label or nomenclature.label_default
