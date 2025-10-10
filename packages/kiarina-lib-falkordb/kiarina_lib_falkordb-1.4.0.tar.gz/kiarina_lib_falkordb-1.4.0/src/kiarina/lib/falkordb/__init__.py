import logging
from importlib import import_module
from importlib.metadata import version
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._sync.registry import get_falkordb
    from .settings import settings_manager

__version__ = version("kiarina-lib-falkordb")

__all__ = ["get_falkordb", "settings_manager"]

logging.getLogger(__name__).addHandler(logging.NullHandler())


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

    module_map = {
        "get_falkordb": "._sync.registry",
        "settings_manager": ".settings",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
