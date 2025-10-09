from pydantic import Field
from typing import Annotated
from maleo.enums.status import ListOfDataStatuses, FULL_DATA_STATUSES
from .mixins.filter import Filters
from .mixins.sort import Sorts
from .mixins.parameter import (
    Search,
    UseCache,
)
from .mixins.status import DataStatuses
from .operation.action.status import StatusUpdateOperationAction
from .pagination import BaseFlexiblePagination, BaseStrictPagination


class ReadSingleQuery(
    DataStatuses[ListOfDataStatuses],
    UseCache,
):
    statuses: Annotated[
        ListOfDataStatuses,
        Field(list(FULL_DATA_STATUSES), description="Data statuses", min_length=1),
    ] = list(FULL_DATA_STATUSES)


class BaseReadMultipleQuery(
    Sorts,
    Search,
    DataStatuses[ListOfDataStatuses],
    Filters,
    UseCache,
):
    statuses: Annotated[
        ListOfDataStatuses,
        Field(list(FULL_DATA_STATUSES), description="Data statuses", min_length=1),
    ] = list(FULL_DATA_STATUSES)


class ReadUnpaginatedMultipleQuery(
    BaseFlexiblePagination,
    BaseReadMultipleQuery,
):
    pass


class ReadPaginatedMultipleQuery(
    BaseStrictPagination,
    BaseReadMultipleQuery,
):
    pass


class StatusUpdateBody(StatusUpdateOperationAction):
    pass
