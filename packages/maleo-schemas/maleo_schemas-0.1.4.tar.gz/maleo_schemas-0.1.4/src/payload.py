from pydantic import BaseModel, Field
from typing import Generic, List, Optional, TypeVar
from .data import DataPair, AnyDataT, DataMixin, ModelDataT
from .metadata import MetadataMixin, AnyMetadataT, ModelMetadataT
from .mixins.general import Other
from .pagination import OptionalPaginationT, PaginationT, PaginationMixin


class Payload(
    Other,
    MetadataMixin[AnyMetadataT],
    PaginationMixin[OptionalPaginationT],
    DataMixin[AnyDataT],
    BaseModel,
    Generic[AnyDataT, OptionalPaginationT, AnyMetadataT],
):
    pass


PayloadT = TypeVar("PayloadT", bound=Payload)


class PayloadMixin(BaseModel, Generic[PayloadT]):
    payload: PayloadT = Field(..., description="Payload")


class NoDataPayload(
    Payload[None, None, ModelMetadataT],
    Generic[ModelMetadataT],
):
    data: None = None
    pagination: None = None


class SingleDataPayload(
    Payload[ModelDataT, None, ModelMetadataT],
    Generic[ModelDataT, ModelMetadataT],
):
    pagination: None = None


class CreateSingleDataPayload(
    Payload[DataPair[None, ModelDataT], None, ModelMetadataT],
    Generic[ModelDataT, ModelMetadataT],
):
    pass


class ReadSingleDataPayload(
    Payload[DataPair[ModelDataT, None], None, ModelMetadataT],
    Generic[ModelDataT, ModelMetadataT],
):
    pass


class UpdateSingleDataPayload(
    Payload[DataPair[ModelDataT, ModelDataT], None, ModelMetadataT],
    Generic[ModelDataT, ModelMetadataT],
):
    pass


class DeleteSingleDataPayload(
    Payload[DataPair[ModelDataT, None], None, ModelMetadataT],
    Generic[ModelDataT, ModelMetadataT],
):
    pass


class OptionalSingleDataPayload(
    Payload[Optional[ModelDataT], None, ModelMetadataT],
    Generic[ModelDataT, ModelMetadataT],
):
    pagination: None = None


class MultipleDataPayload(
    Payload[List[ModelDataT], PaginationT, ModelMetadataT],
    Generic[ModelDataT, PaginationT, ModelMetadataT],
):
    pass


class CreateMultipleDataPayload(
    Payload[DataPair[None, List[ModelDataT]], PaginationT, ModelMetadataT],
    Generic[ModelDataT, PaginationT, ModelMetadataT],
):
    pass


class ReadMultipleDataPayload(
    Payload[DataPair[List[ModelDataT], None], PaginationT, ModelMetadataT],
    Generic[ModelDataT, PaginationT, ModelMetadataT],
):
    pass


class UpdateMultipleDataPayload(
    Payload[DataPair[List[ModelDataT], List[ModelDataT]], PaginationT, ModelMetadataT],
    Generic[ModelDataT, PaginationT, ModelMetadataT],
):
    pass


class DeleteMultipleDataPayload(
    Payload[DataPair[List[ModelDataT], None], PaginationT, ModelMetadataT],
    Generic[ModelDataT, PaginationT, ModelMetadataT],
):
    pass


class OptionalMultipleDataPayload(
    Payload[Optional[List[ModelDataT]], PaginationT, ModelMetadataT],
    Generic[ModelDataT, PaginationT, ModelMetadataT],
):
    pass
