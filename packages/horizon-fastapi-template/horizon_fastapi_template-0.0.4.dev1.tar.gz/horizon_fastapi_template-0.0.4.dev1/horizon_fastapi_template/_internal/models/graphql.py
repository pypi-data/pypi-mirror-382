from typing import Callable, Dict

import strawberry
from pydantic import BaseModel, Field
from strawberry.fastapi import BaseContext


@strawberry.type
class Query:
    @strawberry.field(description="A simple hello world field.")
    async def hello(self, name: str) -> str:
        return f"Hello {name}!"


class GraphQLVersion(BaseModel):
    version: str = Field(
        pattern=r"^v\d+$",
        description="GraphQL API version in the format 'v' followed by digits (e.g., 'v1', 'v2').",
        default="v1"
    )

    query: type = Field(
        description="Root Query type for GraphQL schema.",
        default=Query
    )

    context_getter: Callable = Field(
        description="Context object for GraphQL requests.",
        default=lambda: BaseContext()
    )



