import importlib
import peewee

from project import settings

MODULE, ENGINE = settings.DB_ENGINE.rsplit('.', 1)
engine = getattr(importlib.import_module(MODULE), ENGINE, None)
if engine:
    params = {k: v for k, v in settings.DB_PARAMS.items() if v is not None}
    db: peewee.Database = engine(**params)
else:
    raise ImportError()
