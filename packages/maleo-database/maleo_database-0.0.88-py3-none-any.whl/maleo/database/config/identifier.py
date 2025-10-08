from pydantic import BaseModel, Field
from typing import Annotated
from maleo.enums.environment import Environment
from maleo.types.dict import OptionalStringToStringDict
from maleo.types.string import OptionalString


class DatabaseIdentifierConfig(BaseModel):
    enabled: Annotated[
        bool, Field(True, description="Whether the database is enabled")
    ] = True
    environment: Annotated[
        Environment, Field(..., description="Database's environment")
    ]
    name: Annotated[str, Field(..., description="Database's name")]
    description: Annotated[
        OptionalString, Field(None, description="Database's description")
    ] = None
    tags: Annotated[
        OptionalStringToStringDict, Field(None, description="Database's tags")
    ] = None
