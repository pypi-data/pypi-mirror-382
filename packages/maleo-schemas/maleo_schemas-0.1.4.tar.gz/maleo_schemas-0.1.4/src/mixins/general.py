from pydantic import BaseModel, Field
from typing import Annotated, Any, Generic
from maleo.types.boolean import BooleanT, OptionalBooleanT
from maleo.types.enum import OptionalStringEnumT
from maleo.types.misc import (
    OptionalFloatOrIntegerT,
    OptionalIntegerOrOptionalStringEnumT,
    StringOrStringEnumT,
    OptionalStringsOrOptionalStringEnumsT,
)
from maleo.types.string import OptionalStringT


class StatusCode(BaseModel):
    status_code: Annotated[int, Field(..., description="Status code", ge=100, le=600)]


class Success(BaseModel, Generic[BooleanT]):
    success: BooleanT = Field(..., description="Success")


class Code(BaseModel, Generic[StringOrStringEnumT]):
    code: StringOrStringEnumT = Field(..., description="Code")


class Codes(BaseModel, Generic[OptionalStringsOrOptionalStringEnumsT]):
    codes: OptionalStringsOrOptionalStringEnumsT = Field(..., description="Codes")


class Message(BaseModel):
    message: str = Field(..., description="Message")


class Description(BaseModel):
    description: str = Field(..., description="Description")


class Descriptor(
    Description, Message, Code[StringOrStringEnumT], Generic[StringOrStringEnumT]
):
    pass


class Order(BaseModel, Generic[OptionalIntegerOrOptionalStringEnumT]):
    order: OptionalIntegerOrOptionalStringEnumT = Field(..., description="Order")


class Level(BaseModel, Generic[OptionalStringEnumT]):
    level: OptionalStringEnumT = Field(..., description="Level")


class Note(BaseModel, Generic[OptionalStringT]):
    note: OptionalStringT = Field(..., description="Note")


class IsDefault(BaseModel, Generic[OptionalBooleanT]):
    is_default: OptionalBooleanT = Field(..., description="Whether is default")


class Other(BaseModel):
    other: Annotated[Any, Field(None, description="Other")] = None


class Age(BaseModel, Generic[OptionalFloatOrIntegerT]):
    age: OptionalFloatOrIntegerT = Field(..., ge=0, description="Age")
