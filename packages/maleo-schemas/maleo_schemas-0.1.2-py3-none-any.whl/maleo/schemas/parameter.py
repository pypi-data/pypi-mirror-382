from pydantic import Field
from typing import Annotated, Generic
from maleo.enums.status import ListOfDataStatuses, FULL_DATA_STATUSES
from maleo.types.enum import StringEnumT
from .mixins.filter import DateFilters
from .mixins.identity import (
    IdentifierValueT,
    IdentifierTypeValue,
)
from .mixins.parameter import (
    Search,
    UseCache,
)
from .mixins.sort import SortColumns
from .mixins.status import DataStatuses
from .operation.action.status import StatusUpdateOperationAction
from .pagination import BaseFlexiblePagination, BaseStrictPagination


class ReadSingleParameter(
    DataStatuses[ListOfDataStatuses],
    UseCache,
    IdentifierTypeValue[StringEnumT, IdentifierValueT],
    Generic[StringEnumT, IdentifierValueT],
):
    statuses: Annotated[
        ListOfDataStatuses,
        Field(list(FULL_DATA_STATUSES), description="Data statuses", min_length=1),
    ] = list(FULL_DATA_STATUSES)


class BaseReadMultipleParameter(
    SortColumns,
    Search,
    DataStatuses[ListOfDataStatuses],
    DateFilters,
    UseCache,
):
    statuses: Annotated[
        ListOfDataStatuses,
        Field(list(FULL_DATA_STATUSES), description="Data statuses", min_length=1),
    ] = list(FULL_DATA_STATUSES)


class ReadUnpaginatedMultipleParameter(
    BaseFlexiblePagination,
    BaseReadMultipleParameter,
):
    pass


class ReadPaginatedMultipleParameter(
    BaseStrictPagination,
    BaseReadMultipleParameter,
):
    pass


class StatusUpdateParameter(
    StatusUpdateOperationAction,
    IdentifierTypeValue[StringEnumT, IdentifierValueT],
    Generic[StringEnumT, IdentifierValueT],
):
    pass


class DeleteSingleParameter(
    IdentifierTypeValue[StringEnumT, IdentifierValueT],
    Generic[StringEnumT, IdentifierValueT],
):
    pass
