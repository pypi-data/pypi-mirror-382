import sys
import inspect
import pkgutil
import importlib
from ..collection import BaseCollection

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points


def list_available_collection_classes():
    for finder, name, ispkg in pkgutil.iter_modules(
        sys.modules[__name__].__path__, sys.modules[__name__].__name__ + "."
    ):
        try:
            module = importlib.import_module(name)
        except Exception:
            continue
        for item in dir(module):
            item = getattr(module, item)
            if (
                inspect.isclass(item)
                and issubclass(item, BaseCollection)
                and not inspect.isabstract(item)
            ):
                yield item
    for entry in entry_points(group="flask_collections"):
        yield entry.load()


def discover_collection_cls(config):
    for collection_cls in list_available_collection_classes():
        if collection_cls.matches_config(config):
            return collection_cls
