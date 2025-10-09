# utils/db_loader.py

from importlib import import_module


def load_all_models():
    """
    Import all models modules to ensure SQLAlchemy registers all tables.
    """
    import_module("igem.db.models.config_models")
    import_module("igem.db.models.etl_models")
    import_module("igem.db.models.ge_models")
