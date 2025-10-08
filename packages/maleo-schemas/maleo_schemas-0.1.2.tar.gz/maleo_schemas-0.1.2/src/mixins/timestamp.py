from datetime import datetime
from pydantic import BaseModel, Field
from typing import Generic, TypeVar
from maleo.types.datetime import OptionalDatetime, OptionalDatetimeT
from maleo.types.float import OptionalFloatT


class FromTimestamp(BaseModel, Generic[OptionalDatetimeT]):
    from_date: OptionalDatetimeT = Field(..., description="From date")


class ToTimestamp(BaseModel, Generic[OptionalDatetimeT]):
    to_date: OptionalDatetimeT = Field(..., description="To date")


class ExecutionTimestamp(BaseModel, Generic[OptionalDatetimeT]):
    executed_at: OptionalDatetimeT = Field(..., description="executed_at timestamp")


class CompletionTimestamp(BaseModel, Generic[OptionalDatetimeT]):
    completed_at: OptionalDatetimeT = Field(..., description="completed_at timestamp")


class CreationTimestamp(BaseModel):
    created_at: datetime = Field(..., description="created_at timestamp")


class UpdateTimestamp(BaseModel):
    updated_at: datetime = Field(..., description="updated_at timestamp")


class LifecycleTimestamp(
    UpdateTimestamp,
    CreationTimestamp,
):
    pass


class DeletionTimestamp(BaseModel, Generic[OptionalDatetimeT]):
    deleted_at: OptionalDatetimeT = Field(..., description="deleted_at timestamp")


class RestorationTimestamp(BaseModel, Generic[OptionalDatetimeT]):
    restored_at: OptionalDatetimeT = Field(..., description="restored_at timestamp")


class DeactivationTimestamp(BaseModel, Generic[OptionalDatetimeT]):
    deactivated_at: OptionalDatetimeT = Field(
        ..., description="deactivated_at timestamp"
    )


class ActivationTimestamp(BaseModel, Generic[OptionalDatetimeT]):
    activated_at: OptionalDatetimeT = Field(..., description="activated_at timestamp")


DeletionTimestampT = TypeVar("DeletionTimestampT", bound=OptionalDatetime)
RestorationTimestampT = TypeVar("RestorationTimestampT", bound=OptionalDatetime)
DeactivationTimestampT = TypeVar("DeactivationTimestampT", bound=OptionalDatetime)
ActivationTimestampT = TypeVar("ActivationTimestampT", bound=OptionalDatetime)


class StatusTimestamp(
    ActivationTimestamp[ActivationTimestampT],
    DeactivationTimestamp[DeactivationTimestampT],
    RestorationTimestamp[RestorationTimestampT],
    DeletionTimestamp[DeletionTimestampT],
    Generic[
        DeletionTimestampT,
        RestorationTimestampT,
        DeactivationTimestampT,
        ActivationTimestampT,
    ],
):
    pass


class DataStatusTimestamp(
    StatusTimestamp[
        OptionalDatetime,
        OptionalDatetime,
        OptionalDatetime,
        datetime,
    ],
):
    pass


class DataTimestamp(
    DataStatusTimestamp,
    LifecycleTimestamp,
):
    pass


class Duration(BaseModel, Generic[OptionalFloatT]):
    duration: OptionalFloatT = Field(..., description="Duration")


class InferenceDuration(BaseModel, Generic[OptionalFloatT]):
    inference_duration: OptionalFloatT = Field(..., description="Inference duration")
