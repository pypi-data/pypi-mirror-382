"""Router registration for the FastAPI Template application."""
from pathlib import Path
from typing import List

from fastapi import FastAPI

from .metrics import metrics_router
from .probes import health_router
from .swagger import router as swagger_router
from .qraphql import create_graphql_router
from ..models import GraphQLVersion


def add_routers(
    app: FastAPI,
    *,
    enable_swagger: bool = True,
    enable_metrics: bool = True,
    enable_probe: bool = True,
) -> None:
    """Attach optional routers to the application."""

    if enable_swagger:
        app.include_router(swagger_router, include_in_schema=False)

    if enable_metrics:
        app.include_router(metrics_router, include_in_schema=False)

    if enable_probe:
        app.include_router(health_router, include_in_schema=False)


def add_graphql_routes(app: FastAPI, versions: List[GraphQLVersion], static_files: Path) -> None:
    """Attach GraphQL routes to the application."""

    for version in versions:
        app.include_router(create_graphql_router(version, static_files), include_in_schema=True)

