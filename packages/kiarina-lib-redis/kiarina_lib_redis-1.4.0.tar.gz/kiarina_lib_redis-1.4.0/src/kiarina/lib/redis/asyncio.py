import logging
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._async.registry import get_redis
    from .settings import settings_manager

__all__ = ["get_redis", "settings_manager"]

logging.getLogger(__name__).addHandler(logging.NullHandler())


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

    module_map = {
        "get_redis": "._async.registry",
        "settings_manager": ".settings",
    }

    parent = __name__.rsplit(".", 1)[0]
    globals()[name] = getattr(import_module(module_map[name], parent), name)
    return globals()[name]
