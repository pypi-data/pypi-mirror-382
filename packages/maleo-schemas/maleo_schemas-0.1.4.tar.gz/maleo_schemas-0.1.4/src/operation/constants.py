from typing import Mapping
from maleo.enums.status import DataStatus, SequenceOfDataStatuses
from .enums import ResourceOperationStatusUpdateType


STATUS_UPDATE_RULES: Mapping[
    ResourceOperationStatusUpdateType, SequenceOfDataStatuses
] = {
    ResourceOperationStatusUpdateType.DELETE: (DataStatus.INACTIVE, DataStatus.ACTIVE),
    ResourceOperationStatusUpdateType.RESTORE: (DataStatus.DELETED,),
    ResourceOperationStatusUpdateType.DEACTIVATE: (DataStatus.ACTIVE,),
    ResourceOperationStatusUpdateType.ACTIVATE: (DataStatus.INACTIVE,),
}

STATUS_UPDATE_RESULT: Mapping[ResourceOperationStatusUpdateType, DataStatus] = {
    ResourceOperationStatusUpdateType.DELETE: DataStatus.DELETED,
    ResourceOperationStatusUpdateType.RESTORE: DataStatus.ACTIVE,
    ResourceOperationStatusUpdateType.DEACTIVATE: DataStatus.INACTIVE,
    ResourceOperationStatusUpdateType.ACTIVATE: DataStatus.ACTIVE,
}
