from pydantic import BaseModel, Field
from typing import Annotated, Generic
from maleo.types.dict import OptionalStringToAnyDict
from maleo.types.enum import StringEnumT


class BaseOperationAction(BaseModel, Generic[StringEnumT]):
    type: Annotated[StringEnumT, Field(..., description="Action's type")]


class SimpleOperationAction(BaseOperationAction[StringEnumT], Generic[StringEnumT]):
    details: Annotated[
        OptionalStringToAnyDict, Field(None, description="Action's details")
    ] = None
