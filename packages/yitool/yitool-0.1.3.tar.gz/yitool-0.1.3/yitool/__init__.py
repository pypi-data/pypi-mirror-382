# -*- coding: utf-8 -*-
"""导出公共接口"""

from yitool.const import __VERSION__
import importlib
import typing

__version__ = __VERSION__

__all__ = [
    "shared",
    "utils",
    "db",
    "misc",
    "cli",
    "const",
    "enums",
    "exceptions",
    "log",
    "yi_db",
    "yi_redis",
]


# Copied from https://peps.python.org/pep-0562/
def __getattr__(name: str) -> typing.Any:
    if name in __all__:
        return importlib.import_module("." + name, __name__)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
