"""Pydantic models used internally by the FastAPI Template package."""

from .handler import ExceptionHandlerConfig
from .graphql import GraphQLVersion

__all__ = ["ExceptionHandlerConfig", "GraphQLVersion"]
