from enum import StrEnum
from fastapi import Header
from fastapi.requests import HTTPConnection, Request
from fastapi.websockets import WebSocket
from pydantic import BaseModel, Field
from typing import (
    Annotated,
    Callable,
    Generic,
    Literal,
    Optional,
    TypeVar,
    Union,
    overload,
)
from uuid import UUID
from maleo.enums.connection import Header as HeaderEnum, Protocol as ProtocolEnum
from maleo.types.string import ListOfStrings
from maleo.types.uuid import OptionalUUID


class Source(StrEnum):
    HEADER = "header"
    STATE = "state"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


class Impersonation(BaseModel):
    user_id: Annotated[UUID, Field(..., description="User's ID")]
    organization_id: Annotated[
        OptionalUUID, Field(None, description="Organization's ID")
    ] = None

    @classmethod
    def extract(cls, conn: HTTPConnection) -> Optional["Impersonation"]:
        impersonation = getattr(conn.state, "impersonation", None)
        if isinstance(impersonation, Impersonation):
            return impersonation

        user_id = conn.headers.get(HeaderEnum.X_USER_ID, None)
        if user_id is not None:
            user_id = UUID(user_id)

        organization_id = conn.headers.get(HeaderEnum.X_ORGANIZATION_ID, None)
        if organization_id is not None:
            organization_id = UUID(organization_id)

        if user_id is not None:
            return cls(
                user_id=user_id,
                organization_id=organization_id,
            )

        return None

    @overload
    @classmethod
    def as_dependency(
        cls,
        protocol: None = None,
        /,
    ) -> Callable[
        [HTTPConnection, OptionalUUID, OptionalUUID], Optional["Impersonation"]
    ]: ...
    @overload
    @classmethod
    def as_dependency(
        cls,
        protocol: Literal[ProtocolEnum.HTTP],
        /,
    ) -> Callable[[Request, OptionalUUID, OptionalUUID], Optional["Impersonation"]]: ...
    @overload
    @classmethod
    def as_dependency(
        cls,
        protocol: Literal[ProtocolEnum.WEBSOCKET],
        /,
    ) -> Callable[[WebSocket], Optional["Impersonation"]]: ...
    @classmethod
    def as_dependency(
        cls,
        protocol: Optional[ProtocolEnum] = None,
        /,
    ) -> Union[
        Callable[
            [HTTPConnection, OptionalUUID, OptionalUUID], Optional["Impersonation"]
        ],
        Callable[[Request, OptionalUUID, OptionalUUID], Optional["Impersonation"]],
        Callable[[WebSocket], Optional["Impersonation"]],
    ]:
        def _dependency(
            conn: HTTPConnection,
            # These are for documentation purpose only
            user_id: OptionalUUID = Header(
                None,
                alias=HeaderEnum.X_USER_ID.value,
                description="User's ID",
            ),
            organization_id: OptionalUUID = Header(
                None,
                alias=HeaderEnum.X_ORGANIZATION_ID.value,
                description="Organization's ID",
            ),
        ) -> Optional["Impersonation"]:
            return cls.extract(conn)

        def _request_dependency(
            request: Request,
            # These are for documentation purpose only
            user_id: OptionalUUID = Header(
                None,
                alias=HeaderEnum.X_USER_ID.value,
                description="User's ID",
            ),
            organization_id: OptionalUUID = Header(
                None,
                alias=HeaderEnum.X_ORGANIZATION_ID.value,
                description="Organization's ID",
            ),
        ) -> Optional["Impersonation"]:
            return cls.extract(request)

        def _websocket_dependency(websocket: WebSocket) -> Optional["Impersonation"]:
            return cls.extract(websocket)

        if protocol is None:
            return _dependency
        elif protocol is ProtocolEnum.HTTP:
            return _request_dependency
        elif protocol is ProtocolEnum.WEBSOCKET:
            return _websocket_dependency


OptionalImpersonation = Optional[Impersonation]
OptionalImpersonationT = TypeVar("OptionalImpersonationT", bound=OptionalImpersonation)


class ImpersonationMixin(BaseModel, Generic[OptionalImpersonationT]):
    impersonation: OptionalImpersonationT = Field(..., description="Impersonation")
