from pydantic import BaseModel, Field
from typing import Generic
from maleo.types.boolean import OptionalBooleanT


class IsRoot(BaseModel, Generic[OptionalBooleanT]):
    is_root: OptionalBooleanT = Field(..., description="Whether is root")


class IsParent(BaseModel, Generic[OptionalBooleanT]):
    is_parent: OptionalBooleanT = Field(..., description="Whether is parent")


class IsChild(BaseModel, Generic[OptionalBooleanT]):
    is_child: OptionalBooleanT = Field(..., description="Whether is child")


class IsLeaf(BaseModel, Generic[OptionalBooleanT]):
    is_leaf: OptionalBooleanT = Field(..., description="Whether is leaf")
