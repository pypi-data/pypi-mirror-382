import httpx
from typing import Any, Literal, Optional, Type, Union, overload
from maleo.logging.enums import Level
from maleo.logging.logger import EnvironmentT, ServiceKeyT, Base
from maleo.types.string import OptionalString
from maleo.types.uuid import OptionalUUID
from ..application import OptionalApplicationContext
from ..connection import ConnectionContext, OptionalConnectionContext
from ..error.enums import Code as ErrorCode
from ..operation.context import Context
from ..operation.enums import OperationType
from ..operation.mixins import OptionalTimestamp
from ..operation.action.resource import AnyResourceOperationAction
from ..operation.action.system import SystemOperationAction
from ..operation.action.websocket import WebSocketOperationAction
from ..resource import Resource, OptionalResource
from ..response import (
    BadRequestResponse,
    UnauthorizedResponse,
    ForbiddenResponse,
    NotFoundResponse,
    MethodNotAllowedResponse,
    ConflictResponse,
    UnprocessableEntityResponse,
    TooManyRequestsResponse,
    InternalServerErrorResponse,
    NotImplementedResponse,
    BadGatewayResponse,
    ServiceUnavailableResponse,
    OptionalAnyErrorResponse,
    ErrorFactory as ErrorResponseFactory,
)
from ..security.authentication import OptionalAnyAuthentication
from ..security.authorization import OptionalAnyAuthorization
from ..security.impersonation import OptionalImpersonation
from .exc import (
    BadRequest,
    Unauthorized,
    Forbidden,
    NotFound,
    MethodNotAllowed,
    Conflict,
    UnprocessableEntity,
    TooManyRequests,
    InternalServerError,
    NotImplemented,
    BadGateway,
    ServiceUnavailable,
    AnyExceptionType,
    AnyException,
)


class Factory:
    @overload
    @classmethod
    def cls_from_code(
        cls,
        code: Literal[ErrorCode.BAD_REQUEST, 400],
        /,
    ) -> Type[BadRequest]: ...
    @overload
    @classmethod
    def cls_from_code(
        cls,
        code: Literal[ErrorCode.UNAUTHORIZED, 401],
        /,
    ) -> Type[Unauthorized]: ...
    @overload
    @classmethod
    def cls_from_code(
        cls,
        code: Literal[ErrorCode.FORBIDDEN, 403],
        /,
    ) -> Type[Forbidden]: ...
    @overload
    @classmethod
    def cls_from_code(
        cls,
        code: Literal[ErrorCode.NOT_FOUND, 404],
        /,
    ) -> Type[NotFound]: ...
    @overload
    @classmethod
    def cls_from_code(
        cls,
        code: Literal[ErrorCode.METHOD_NOT_ALLOWED, 405],
        /,
    ) -> Type[MethodNotAllowed]: ...
    @overload
    @classmethod
    def cls_from_code(
        cls,
        code: Literal[ErrorCode.CONFLICT, 409],
        /,
    ) -> Type[Conflict]: ...
    @overload
    @classmethod
    def cls_from_code(
        cls,
        code: Literal[ErrorCode.UNPROCESSABLE_ENTITY, 422],
        /,
    ) -> Type[UnprocessableEntity]: ...
    @overload
    @classmethod
    def cls_from_code(
        cls,
        code: Literal[ErrorCode.TOO_MANY_REQUESTS, 429],
        /,
    ) -> Type[TooManyRequests]: ...
    @overload
    @classmethod
    def cls_from_code(
        cls,
        code: Literal[ErrorCode.INTERNAL_SERVER_ERROR, 500],
        /,
    ) -> Type[InternalServerError]: ...
    @overload
    @classmethod
    def cls_from_code(
        cls,
        code: Literal[ErrorCode.NOT_IMPLEMENTED, 501],
        /,
    ) -> Type[NotImplemented]: ...
    @overload
    @classmethod
    def cls_from_code(
        cls,
        code: Literal[ErrorCode.BAD_GATEWAY, 502],
        /,
    ) -> Type[BadGateway]: ...
    @overload
    @classmethod
    def cls_from_code(
        cls,
        code: Literal[ErrorCode.SERVICE_UNAVAILABLE, 503],
        /,
    ) -> Type[ServiceUnavailable]: ...
    @overload
    @classmethod
    def cls_from_code(
        cls,
        code: Union[ErrorCode, int],
        /,
    ) -> AnyExceptionType: ...
    @classmethod
    def cls_from_code(
        cls,
        code: Union[ErrorCode, int],
        /,
    ) -> AnyExceptionType:
        if code is ErrorCode.BAD_REQUEST or code == 400:
            return BadRequest
        elif code is ErrorCode.UNAUTHORIZED or code == 401:
            return Unauthorized
        elif code is ErrorCode.FORBIDDEN or code == 403:
            return Forbidden
        elif code is ErrorCode.NOT_FOUND or code == 404:
            return NotFound
        elif code is ErrorCode.METHOD_NOT_ALLOWED or code == 405:
            return MethodNotAllowed
        elif code is ErrorCode.CONFLICT or code == 409:
            return Conflict
        elif code is ErrorCode.UNPROCESSABLE_ENTITY or code == 422:
            return UnprocessableEntity
        elif code is ErrorCode.TOO_MANY_REQUESTS or code == 429:
            return TooManyRequests
        elif code is ErrorCode.INTERNAL_SERVER_ERROR or code == 500:
            return InternalServerError
        elif code is ErrorCode.NOT_IMPLEMENTED or code == 501:
            return NotImplemented
        elif code is ErrorCode.BAD_GATEWAY or code == 502:
            return BadGateway
        elif code is ErrorCode.SERVICE_UNAVAILABLE or code == 503:
            return ServiceUnavailable
        raise ValueError(
            f"Unable to determine response and exception class for code: {code}"
        )

    # Specific code, request operation
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.BAD_REQUEST, 400],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.REQUEST],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[BadRequestResponse] = None,
    ) -> BadRequest: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.UNAUTHORIZED, 401],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.REQUEST],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[UnauthorizedResponse] = None,
    ) -> Unauthorized: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.FORBIDDEN, 403],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.REQUEST],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[ForbiddenResponse] = None,
    ) -> Forbidden: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.NOT_FOUND, 404],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.REQUEST],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[NotFoundResponse] = None,
    ) -> NotFound: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.METHOD_NOT_ALLOWED, 405],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.REQUEST],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[MethodNotAllowedResponse] = None,
    ) -> MethodNotAllowed: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.CONFLICT, 409],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.REQUEST],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[ConflictResponse] = None,
    ) -> Conflict: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.UNPROCESSABLE_ENTITY, 422],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.REQUEST],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[UnprocessableEntityResponse] = None,
    ) -> UnprocessableEntity: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.TOO_MANY_REQUESTS, 429],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.REQUEST],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[TooManyRequestsResponse] = None,
    ) -> TooManyRequests: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.INTERNAL_SERVER_ERROR, 500],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.REQUEST],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[InternalServerErrorResponse] = None,
    ) -> InternalServerError: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.NOT_IMPLEMENTED, 501],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.REQUEST],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[NotImplementedResponse] = None,
    ) -> NotImplemented: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.BAD_GATEWAY, 502],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.REQUEST],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[BadGatewayResponse] = None,
    ) -> BadGateway: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.SERVICE_UNAVAILABLE, 503],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.REQUEST],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[ServiceUnavailableResponse] = None,
    ) -> ServiceUnavailable: ...

    # Specific code, resource operation
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.BAD_REQUEST, 400],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.RESOURCE],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        resource: Resource,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[BadRequestResponse] = None,
    ) -> BadRequest: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.UNAUTHORIZED, 401],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.RESOURCE],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        resource: Resource,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[UnauthorizedResponse] = None,
    ) -> Unauthorized: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.FORBIDDEN, 403],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.RESOURCE],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        resource: Resource,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[ForbiddenResponse] = None,
    ) -> Forbidden: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.NOT_FOUND, 404],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.RESOURCE],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        resource: Resource,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[NotFoundResponse] = None,
    ) -> NotFound: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.METHOD_NOT_ALLOWED, 405],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.RESOURCE],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        resource: Resource,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[MethodNotAllowedResponse] = None,
    ) -> MethodNotAllowed: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.CONFLICT, 409],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.RESOURCE],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        resource: Resource,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[ConflictResponse] = None,
    ) -> Conflict: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.UNPROCESSABLE_ENTITY, 422],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.RESOURCE],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        resource: Resource,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[UnprocessableEntityResponse] = None,
    ) -> UnprocessableEntity: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.TOO_MANY_REQUESTS, 429],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.RESOURCE],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        resource: Resource,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[TooManyRequestsResponse] = None,
    ) -> TooManyRequests: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.INTERNAL_SERVER_ERROR, 500],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.RESOURCE],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        resource: Resource,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[InternalServerErrorResponse] = None,
    ) -> InternalServerError: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.NOT_IMPLEMENTED, 501],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.RESOURCE],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        resource: Resource,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[NotImplementedResponse] = None,
    ) -> NotImplemented: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.BAD_GATEWAY, 502],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.RESOURCE],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        resource: Resource,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[BadGatewayResponse] = None,
    ) -> BadGateway: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.SERVICE_UNAVAILABLE, 503],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.RESOURCE],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        resource: Resource,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[ServiceUnavailableResponse] = None,
    ) -> ServiceUnavailable: ...

    # Specific code, request or resource operation
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.BAD_REQUEST, 400],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.REQUEST, OperationType.RESOURCE],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        resource: OptionalResource = None,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[BadRequestResponse] = None,
    ) -> BadRequest: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.UNAUTHORIZED, 401],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.REQUEST, OperationType.RESOURCE],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        resource: OptionalResource = None,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[UnauthorizedResponse] = None,
    ) -> Unauthorized: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.FORBIDDEN, 403],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.REQUEST, OperationType.RESOURCE],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        resource: OptionalResource = None,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[ForbiddenResponse] = None,
    ) -> Forbidden: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.NOT_FOUND, 404],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.REQUEST, OperationType.RESOURCE],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        resource: OptionalResource = None,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[NotFoundResponse] = None,
    ) -> NotFound: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.METHOD_NOT_ALLOWED, 405],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.REQUEST, OperationType.RESOURCE],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        resource: OptionalResource = None,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[MethodNotAllowedResponse] = None,
    ) -> MethodNotAllowed: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.CONFLICT, 409],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.REQUEST, OperationType.RESOURCE],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        resource: OptionalResource = None,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[ConflictResponse] = None,
    ) -> Conflict: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.UNPROCESSABLE_ENTITY, 422],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.REQUEST, OperationType.RESOURCE],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        resource: OptionalResource = None,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[UnprocessableEntityResponse] = None,
    ) -> UnprocessableEntity: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.TOO_MANY_REQUESTS, 429],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.REQUEST, OperationType.RESOURCE],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        resource: OptionalResource = None,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[TooManyRequestsResponse] = None,
    ) -> TooManyRequests: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.INTERNAL_SERVER_ERROR, 500],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.REQUEST, OperationType.RESOURCE],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        resource: OptionalResource = None,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[InternalServerErrorResponse] = None,
    ) -> InternalServerError: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.NOT_IMPLEMENTED, 501],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.REQUEST, OperationType.RESOURCE],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        resource: OptionalResource = None,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[NotImplementedResponse] = None,
    ) -> NotImplemented: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.BAD_GATEWAY, 502],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.REQUEST, OperationType.RESOURCE],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        resource: OptionalResource = None,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[BadGatewayResponse] = None,
    ) -> BadGateway: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.SERVICE_UNAVAILABLE, 503],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.REQUEST, OperationType.RESOURCE],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        resource: OptionalResource = None,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[ServiceUnavailableResponse] = None,
    ) -> ServiceUnavailable: ...

    # Specific code, system operation
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.BAD_REQUEST, 400],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.SYSTEM],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: SystemOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[BadRequestResponse] = None,
    ) -> BadRequest: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.UNAUTHORIZED, 401],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.SYSTEM],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: SystemOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[UnauthorizedResponse] = None,
    ) -> Unauthorized: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.FORBIDDEN, 403],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.SYSTEM],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: SystemOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[ForbiddenResponse] = None,
    ) -> Forbidden: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.NOT_FOUND, 404],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.SYSTEM],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: SystemOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[NotFoundResponse] = None,
    ) -> NotFound: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.METHOD_NOT_ALLOWED, 405],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.SYSTEM],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: SystemOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[MethodNotAllowedResponse] = None,
    ) -> MethodNotAllowed: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.CONFLICT, 409],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.SYSTEM],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: SystemOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[ConflictResponse] = None,
    ) -> Conflict: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.UNPROCESSABLE_ENTITY, 422],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.SYSTEM],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: SystemOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[UnprocessableEntityResponse] = None,
    ) -> UnprocessableEntity: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.TOO_MANY_REQUESTS, 429],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.SYSTEM],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: SystemOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[TooManyRequestsResponse] = None,
    ) -> TooManyRequests: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.INTERNAL_SERVER_ERROR, 500],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.SYSTEM],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: SystemOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[InternalServerErrorResponse] = None,
    ) -> InternalServerError: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.NOT_IMPLEMENTED, 501],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.SYSTEM],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: SystemOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[NotImplementedResponse] = None,
    ) -> NotImplemented: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.BAD_GATEWAY, 502],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.SYSTEM],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: SystemOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[BadGatewayResponse] = None,
    ) -> BadGateway: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.SERVICE_UNAVAILABLE, 503],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.SYSTEM],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: SystemOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[ServiceUnavailableResponse] = None,
    ) -> ServiceUnavailable: ...

    # Specific code, websocket operation
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.BAD_REQUEST, 400],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.WEBSOCKET],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: WebSocketOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[BadRequestResponse] = None,
    ) -> BadRequest: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.UNAUTHORIZED, 401],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.WEBSOCKET],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: WebSocketOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[UnauthorizedResponse] = None,
    ) -> Unauthorized: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.FORBIDDEN, 403],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.WEBSOCKET],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: WebSocketOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[ForbiddenResponse] = None,
    ) -> Forbidden: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.NOT_FOUND, 404],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.WEBSOCKET],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: WebSocketOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[NotFoundResponse] = None,
    ) -> NotFound: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.METHOD_NOT_ALLOWED, 405],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.WEBSOCKET],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: WebSocketOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[MethodNotAllowedResponse] = None,
    ) -> MethodNotAllowed: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.CONFLICT, 409],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.WEBSOCKET],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: WebSocketOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[ConflictResponse] = None,
    ) -> Conflict: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.UNPROCESSABLE_ENTITY, 422],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.WEBSOCKET],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: WebSocketOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[UnprocessableEntityResponse] = None,
    ) -> UnprocessableEntity: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.TOO_MANY_REQUESTS, 429],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.WEBSOCKET],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: WebSocketOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[TooManyRequestsResponse] = None,
    ) -> TooManyRequests: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.INTERNAL_SERVER_ERROR, 500],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.WEBSOCKET],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: WebSocketOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[InternalServerErrorResponse] = None,
    ) -> InternalServerError: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.NOT_IMPLEMENTED, 501],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.WEBSOCKET],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: WebSocketOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[NotImplementedResponse] = None,
    ) -> NotImplemented: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.BAD_GATEWAY, 502],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.WEBSOCKET],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: WebSocketOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[BadGatewayResponse] = None,
    ) -> BadGateway: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.SERVICE_UNAVAILABLE, 503],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.WEBSOCKET],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: WebSocketOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[ServiceUnavailableResponse] = None,
    ) -> ServiceUnavailable: ...

    # Specific code, any operation_type
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.BAD_REQUEST, 400],
        *args: object,
        details: Any = None,
        operation_type: OperationType,
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: Union[AnyResourceOperationAction, SystemOperationAction],
        resource: OptionalResource = None,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[BadRequestResponse] = None,
    ) -> BadRequest: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.UNAUTHORIZED, 401],
        *args: object,
        details: Any = None,
        operation_type: OperationType,
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: Union[AnyResourceOperationAction, SystemOperationAction],
        resource: OptionalResource = None,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[UnauthorizedResponse] = None,
    ) -> Unauthorized: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.FORBIDDEN, 403],
        *args: object,
        details: Any = None,
        operation_type: OperationType,
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: Union[AnyResourceOperationAction, SystemOperationAction],
        resource: OptionalResource = None,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[ForbiddenResponse] = None,
    ) -> Forbidden: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.NOT_FOUND, 404],
        *args: object,
        details: Any = None,
        operation_type: OperationType,
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: Union[AnyResourceOperationAction, SystemOperationAction],
        resource: OptionalResource = None,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[NotFoundResponse] = None,
    ) -> NotFound: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.METHOD_NOT_ALLOWED, 405],
        *args: object,
        details: Any = None,
        operation_type: OperationType,
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: Union[AnyResourceOperationAction, SystemOperationAction],
        resource: OptionalResource = None,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[MethodNotAllowedResponse] = None,
    ) -> MethodNotAllowed: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.CONFLICT, 409],
        *args: object,
        details: Any = None,
        operation_type: OperationType,
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: Union[AnyResourceOperationAction, SystemOperationAction],
        resource: OptionalResource = None,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[ConflictResponse] = None,
    ) -> Conflict: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.UNPROCESSABLE_ENTITY, 422],
        *args: object,
        details: Any = None,
        operation_type: OperationType,
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: Union[AnyResourceOperationAction, SystemOperationAction],
        resource: OptionalResource = None,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[UnprocessableEntityResponse] = None,
    ) -> UnprocessableEntity: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.TOO_MANY_REQUESTS, 429],
        *args: object,
        details: Any = None,
        operation_type: OperationType,
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: Union[AnyResourceOperationAction, SystemOperationAction],
        resource: OptionalResource = None,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[TooManyRequestsResponse] = None,
    ) -> TooManyRequests: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.INTERNAL_SERVER_ERROR, 500],
        *args: object,
        details: Any = None,
        operation_type: OperationType,
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: Union[AnyResourceOperationAction, SystemOperationAction],
        resource: OptionalResource = None,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[InternalServerErrorResponse] = None,
    ) -> InternalServerError: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.NOT_IMPLEMENTED, 501],
        *args: object,
        details: Any = None,
        operation_type: OperationType,
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: Union[AnyResourceOperationAction, SystemOperationAction],
        resource: OptionalResource = None,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[NotImplementedResponse] = None,
    ) -> NotImplemented: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.BAD_GATEWAY, 502],
        *args: object,
        details: Any = None,
        operation_type: OperationType,
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: Union[AnyResourceOperationAction, SystemOperationAction],
        resource: OptionalResource = None,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[BadGatewayResponse] = None,
    ) -> BadGateway: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Literal[ErrorCode.SERVICE_UNAVAILABLE, 503],
        *args: object,
        details: Any = None,
        operation_type: OperationType,
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: Union[AnyResourceOperationAction, SystemOperationAction],
        resource: OptionalResource = None,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: Optional[ServiceUnavailableResponse] = None,
    ) -> ServiceUnavailable: ...

    # Any code, specific operation_type
    @overload
    @classmethod
    def from_code(
        cls,
        code: Union[ErrorCode, int],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.REQUEST],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: ConnectionContext,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: OptionalAnyErrorResponse = None,
    ) -> AnyException: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Union[ErrorCode, int],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.RESOURCE],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        resource: Resource,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: OptionalAnyErrorResponse = None,
    ) -> AnyException: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Union[ErrorCode, int],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.REQUEST, OperationType.RESOURCE],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        resource: OptionalResource = None,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: OptionalAnyErrorResponse = None,
    ) -> AnyException: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Union[ErrorCode, int],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.SYSTEM],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: SystemOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: OptionalAnyErrorResponse = None,
    ) -> AnyException: ...
    @overload
    @classmethod
    def from_code(
        cls,
        code: Union[ErrorCode, int],
        *args: object,
        details: Any = None,
        operation_type: Literal[OperationType.WEBSOCKET],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: WebSocketOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: OptionalAnyErrorResponse = None,
    ) -> AnyException: ...

    # Catch all
    @overload
    @classmethod
    def from_code(
        cls,
        code: Union[ErrorCode, int],
        *args: object,
        details: Any = None,
        operation_type: OperationType,
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: Union[AnyResourceOperationAction, SystemOperationAction],
        resource: OptionalResource = None,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: OptionalAnyErrorResponse = None,
    ) -> AnyException: ...
    @classmethod
    def from_code(
        cls,
        code: Union[ErrorCode, int],
        *args: object,
        details: Any = None,
        operation_type: OperationType,
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: Union[
            AnyResourceOperationAction,
            SystemOperationAction,
            WebSocketOperationAction,
        ],
        resource: OptionalResource = None,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        response: OptionalAnyErrorResponse = None,
    ) -> AnyException:
        exception_cls = cls.cls_from_code(code)

        exception = exception_cls(
            *args,
            details=details,
            operation_type=operation_type,
            application_context=application_context,
            operation_id=operation_id,
            operation_context=operation_context,
            operation_action=operation_action,
            resource=resource,
            operation_timestamp=operation_timestamp,
            operation_summary=operation_summary,
            connection_context=connection_context,
            authentication=authentication,
            authorization=authorization,
            impersonation=impersonation,
            response=response,
        )

        return exception

    @overload
    @classmethod
    def from_httpx(
        cls,
        response: httpx.Response,
        *,
        operation_type: Literal[OperationType.REQUEST],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        logger: Base[EnvironmentT, ServiceKeyT],
    ) -> AnyException: ...
    @overload
    @classmethod
    def from_httpx(
        cls,
        response: httpx.Response,
        *,
        operation_type: Literal[OperationType.RESOURCE],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        resource: Resource,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        logger: Base[EnvironmentT, ServiceKeyT],
    ) -> AnyException: ...
    @classmethod
    def from_httpx(
        cls,
        response: httpx.Response,
        *,
        operation_type: Literal[OperationType.REQUEST, OperationType.RESOURCE],
        application_context: OptionalApplicationContext = None,
        operation_id: OptionalUUID = None,
        operation_context: Context,
        operation_action: AnyResourceOperationAction,
        resource: OptionalResource = None,
        operation_timestamp: OptionalTimestamp = None,
        operation_summary: OptionalString = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
        logger: Base[EnvironmentT, ServiceKeyT],
    ) -> AnyException:
        if not response.is_error:
            raise ValueError(
                ErrorCode.BAD_REQUEST,
                "Failed generating MaleoException from httpx response, Response is not error",
            )

        response_cls = ErrorResponseFactory.cls_from_code(response.status_code)
        validated_response = response_cls.model_validate(response.json())

        exception = cls.from_code(
            response.status_code,
            details=None,
            operation_type=operation_type,
            application_context=application_context,
            operation_id=operation_id,
            operation_context=operation_context,
            operation_action=operation_action,
            resource=resource,
            operation_timestamp=operation_timestamp,
            operation_summary=operation_summary,
            connection_context=connection_context,
            authentication=authentication,
            authorization=authorization,
            impersonation=impersonation,
            response=validated_response,
        )

        if logger is not None:
            exception.operation.log(logger, Level.ERROR)

        return exception
