from pathlib import Path

import strawberry
from fastapi import APIRouter, HTTPException
from starlette.responses import FileResponse
from strawberry.fastapi import GraphQLRouter

from ..models.graphql import GraphQLVersion

def create_graphql_router(
        version: GraphQLVersion,
        static_files_path: Path
) -> APIRouter:

    schema = strawberry.Schema(query=version.query)

    graphql_app = GraphQLRouter(
        schema,
        prefix=f"/graphql/{version.version}",
        context_getter=version.context_getter,
        graphiql=False
    )

    # Define paths
    static_dir = Path(static_files_path) / "static"
    index_file = Path(static_files_path) / "index.html"

    # Serve the playground HTML
    @graphql_app.get("/playground")
    async def playground():
        if not index_file.exists():
            raise HTTPException(status_code=404, detail="Playground not found")
        return FileResponse(index_file, media_type="text/html")

    # Serve static files under /playground/static
    @graphql_app.get("/playground/static/{file_path:path}")
    async def playground_static(file_path: str):
        file = static_dir / file_path
        if not file.exists() or not file.is_file():
            print(file)
            raise HTTPException(status_code=404, detail="File not found")
        return FileResponse(file)

    return graphql_app