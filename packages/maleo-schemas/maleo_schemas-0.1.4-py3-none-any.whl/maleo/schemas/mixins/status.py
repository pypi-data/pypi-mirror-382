from pydantic import BaseModel, Field
from typing import Generic
from maleo.enums.status import (
    OptionalDataStatusT,
    OptionalListOfDataStatusesT,
)


class DataStatus(BaseModel, Generic[OptionalDataStatusT]):
    status: OptionalDataStatusT = Field(..., description="Data's status")


class DataStatuses(BaseModel, Generic[OptionalListOfDataStatusesT]):
    statuses: OptionalListOfDataStatusesT = Field(..., description="Data's statuses")
