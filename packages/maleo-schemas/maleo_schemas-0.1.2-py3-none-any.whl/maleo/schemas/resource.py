from enum import StrEnum
from pydantic import BaseModel, Field
from typing import Annotated, Generic, List, Literal, Optional, TypeVar, overload
from maleo.types.dict import OptionalStringToAnyDict
from maleo.types.string import ListOfStrings


class AggregateField(StrEnum):
    KEY = "key"
    URL = "slug"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


class ResourceIdentifier(BaseModel):
    key: Annotated[str, Field(..., description="Key", pattern=r"^[a-zA-Z0-9_-]+$")]
    name: Annotated[str, Field(..., description="Name")]
    slug: Annotated[
        str, Field(..., description="URL Slug", pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    ]


class Resource(BaseModel):
    identifiers: Annotated[
        List[ResourceIdentifier], Field(..., min_length=1, description="Identifiers")
    ]
    details: Annotated[OptionalStringToAnyDict, Field(None, description="Details")] = (
        None
    )

    @overload
    def aggregate(
        self, field: Literal[AggregateField.KEY], *, sep: str = ":"
    ) -> str: ...
    @overload
    def aggregate(
        self, field: Literal[AggregateField.URL], *, sep: str = "/"
    ) -> str: ...
    @overload
    def aggregate(
        self, field: AggregateField = AggregateField.KEY, *, sep: str = ":"
    ) -> str: ...
    def aggregate(
        self, field: AggregateField = AggregateField.KEY, *, sep: str = ":"
    ) -> str:
        if field is AggregateField.KEY:
            return sep.join([id.key for id in self.identifiers])
        elif field is AggregateField.URL:
            return sep.join([id.slug for id in self.identifiers])


OptionalResource = Optional[Resource]
OptionalResourceT = TypeVar("OptionalResourceT", bound=OptionalResource)


class ResourceMixin(BaseModel, Generic[OptionalResourceT]):
    resource: OptionalResourceT = Field(..., description="Resource")
