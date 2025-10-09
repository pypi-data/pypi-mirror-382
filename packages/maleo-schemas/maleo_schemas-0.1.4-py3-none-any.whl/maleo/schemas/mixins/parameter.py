from pydantic import BaseModel, Field
from typing import Annotated, Generic
from maleo.types.enum import OptionalListOfStringEnumsT
from maleo.types.string import OptionalString


class Search(BaseModel):
    search: Annotated[OptionalString, Field(None, description="Search string")] = None


class UseCache(BaseModel):
    use_cache: Annotated[bool, Field(True, description="Whether to use cache")] = True


class Include(BaseModel, Generic[OptionalListOfStringEnumsT]):
    include: OptionalListOfStringEnumsT = Field(..., description="Included field(s)")


class Exclude(BaseModel, Generic[OptionalListOfStringEnumsT]):
    exclude: OptionalListOfStringEnumsT = Field(..., description="Excluded field(s)")
