from enum import StrEnum
from pydantic import BaseModel, Field
from typing import Generic, Optional, TypeVar
from maleo.types.string import ListOfStrings


class Domain(StrEnum):
    TENANT = "tenant"
    SYSTEM = "system"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


DomainT = TypeVar("DomainT", bound=Domain)
OptionalDomain = Optional[Domain]
OptionalDomainT = TypeVar("OptionalDomainT", bound=OptionalDomain)


class DomainMixin(BaseModel, Generic[OptionalDomainT]):
    domain: OptionalDomainT = Field(..., description="Domain")
