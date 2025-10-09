from pydantic import BaseModel, Field
from typing import Generic, Optional, TypeVar
from uuid import UUID as PythonUUID
from maleo.types.enum import StringEnumT
from maleo.types.integer import OptionalIntegerT, OptionalListOfIntegersT
from maleo.types.misc import (
    OptionalIntegerOrOptionalUUIDT,
    OptionalIntegersOrOptionalUUIDsT,
)
from maleo.types.string import OptionalStringT, OptionalListOfStringsT
from maleo.types.uuid import OptionalUUIDT, OptionalListOfUUIDsT


class IdentifierType(BaseModel, Generic[StringEnumT]):
    identifier: StringEnumT = Field(..., description="Identifier's type")


IdentifierValueT = TypeVar("IdentifierValueT")


class IdentifierValue(BaseModel, Generic[IdentifierValueT]):
    value: IdentifierValueT = Field(..., description="Identifier's value")


class IdentifierTypeValue(
    IdentifierValue[IdentifierValueT],
    IdentifierType[StringEnumT],
    BaseModel,
    Generic[StringEnumT, IdentifierValueT],
):
    pass


class Id(BaseModel, Generic[OptionalIntegerOrOptionalUUIDT]):
    id: OptionalIntegerOrOptionalUUIDT = Field(..., description="Id")


class IntId(BaseModel, Generic[OptionalIntegerT]):
    id: OptionalIntegerT = Field(..., description="Id (Integer)", ge=1)


class UUIDId(BaseModel, Generic[OptionalUUIDT]):
    id: OptionalUUIDT = Field(..., description="Id (UUID)")


class Ids(BaseModel, Generic[OptionalIntegersOrOptionalUUIDsT]):
    ids: OptionalIntegersOrOptionalUUIDsT = Field(..., description="Ids")


class IntIds(BaseModel, Generic[OptionalListOfIntegersT]):
    ids: OptionalListOfIntegersT = Field(..., description="Ids (Integers)")


class UUIDIds(BaseModel, Generic[OptionalListOfUUIDsT]):
    ids: OptionalListOfUUIDsT = Field(..., description="Ids (UUIDs)")


class UUID(BaseModel, Generic[OptionalUUIDT]):
    uuid: OptionalUUIDT = Field(..., description="UUID")


class UUIDs(BaseModel, Generic[OptionalListOfUUIDsT]):
    uuids: OptionalListOfUUIDsT = Field(..., description="UUIDs")


class DataIdentifier(
    UUID[PythonUUID],
    IntId[int],
):
    pass


class EntityIdentifier(
    UUID[PythonUUID],
    IntId[int],
):
    pass


EntityIdentifierT = TypeVar("EntityIdentifierT", bound=EntityIdentifier)
OptionalEntityIdentifier = Optional[EntityIdentifier]
OptionalEntityIdentifierT = TypeVar(
    "OptionalEntityIdentifierT", bound=OptionalEntityIdentifier
)


class Key(BaseModel, Generic[OptionalStringT]):
    key: OptionalStringT = Field(..., description="Key")


class Keys(BaseModel, Generic[OptionalListOfStringsT]):
    keys: OptionalListOfStringsT = Field(..., description="Keys")


class Name(BaseModel, Generic[OptionalStringT]):
    name: OptionalStringT = Field(..., description="Name")


class Names(BaseModel, Generic[OptionalListOfStringsT]):
    names: OptionalListOfStringsT = Field(..., description="Names")


# ----- ----- ----- Organization ID ----- ----- ----- #


class OrganizationId(BaseModel, Generic[OptionalIntegerOrOptionalUUIDT]):
    organization_id: OptionalIntegerOrOptionalUUIDT = Field(
        ..., description="Organization's ID"
    )


class IntOrganizationId(BaseModel, Generic[OptionalIntegerT]):
    organization_id: OptionalIntegerT = Field(
        ..., description="Organization's ID", ge=1
    )


class UUIDOrganizationId(BaseModel, Generic[OptionalUUIDT]):
    organization_id: OptionalUUIDT = Field(..., description="Organization's ID")


class OrganizationIds(BaseModel, Generic[OptionalIntegersOrOptionalUUIDsT]):
    organization_ids: OptionalIntegersOrOptionalUUIDsT = Field(
        ..., description="Organization's IDs"
    )


class IntOrganizationIds(BaseModel, Generic[OptionalListOfIntegersT]):
    organization_ids: OptionalListOfIntegersT = Field(
        ..., description="Organization's IDs"
    )


class UUIDOrganizationIds(BaseModel, Generic[OptionalListOfUUIDsT]):
    organization_ids: OptionalListOfUUIDsT = Field(
        ..., description="Organization's IDs"
    )


# ----- ----- ----- Parent ID ----- ----- ----- #


class ParentId(BaseModel, Generic[OptionalIntegerT]):
    parent_id: OptionalIntegerT = Field(..., description="Parent's ID", ge=1)


class ParentIds(BaseModel, Generic[OptionalListOfIntegersT]):
    parent_ids: OptionalListOfIntegersT = Field(..., description="Parent's IDs")


# ----- ----- ----- User ID ----- ----- ----- #


class UserId(BaseModel, Generic[OptionalIntegerOrOptionalUUIDT]):
    user_id: OptionalIntegerOrOptionalUUIDT = Field(..., description="User's ID")


class IntUserId(BaseModel, Generic[OptionalIntegerT]):
    user_id: OptionalIntegerT = Field(..., description="User's ID", ge=1)


class UUIDUserId(BaseModel, Generic[OptionalUUIDT]):
    user_id: OptionalUUIDT = Field(..., description="User's ID")


class UserIds(BaseModel, Generic[OptionalIntegersOrOptionalUUIDsT]):
    user_ids: OptionalIntegersOrOptionalUUIDsT = Field(..., description="User's IDs")


class IntUserIds(BaseModel, Generic[OptionalListOfIntegersT]):
    user_ids: OptionalListOfIntegersT = Field(..., description="User's IDs")


class UUIDUserIds(BaseModel, Generic[OptionalListOfUUIDsT]):
    user_ids: OptionalListOfUUIDsT = Field(..., description="User's IDs")
