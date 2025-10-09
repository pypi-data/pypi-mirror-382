"""FastAPI application template package."""
from ._internal import general_create_app

__all__ = ["general_create_app"]


def __getattr__(name: str):
    if name == "general_create_app":
        return general_create_app
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
