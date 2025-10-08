from abc import ABC, abstractmethod
from enum import StrEnum
from fastapi import status, HTTPException
from fastapi.requests import HTTPConnection
from pydantic import BaseModel, ValidationError, Field
from starlette.authentication import (
    AuthCredentials as StarletteCredentials,
    BaseUser as StarletteUser,
)
from typing import (
    Annotated,
    Callable,
    Generic,
    Literal,
    Optional,
    Self,
    TypeGuard,
    TypeVar,
    Union,
    overload,
)
from uuid import UUID
from maleo.types.string import (
    ListOfStrings,
    OptionalListOfStrings,
    OptionalSequenceOfStrings,
)
from maleo.types.uuid import OptionalUUID
from .enums import Domain, OptionalDomain, OptionalDomainT


class ConversionDestination(StrEnum):
    BASE = "base"
    AUTHENTICATED = "authenticated"
    TENANT = "tenant"
    SYSTEM = "system"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


class RequestCredentials(StarletteCredentials):
    def __init__(
        self,
        domain: OptionalDomain = None,
        user_id: OptionalUUID = None,
        organization_id: OptionalUUID = None,
        roles: OptionalSequenceOfStrings = None,
        scopes: OptionalSequenceOfStrings = None,
    ):
        super().__init__(scopes)
        self.domain = domain
        self.user_id = user_id
        self.organization_id = organization_id
        self.roles = [] if roles is None else list(roles)


class RequestUser(StarletteUser):
    def __init__(
        self,
        authenticated: bool = False,
        username: str = "",
        email: str = "",
    ) -> None:
        self._authenticated = authenticated
        self._username = username
        self._email = email

    @property
    def is_authenticated(self) -> bool:
        return self._authenticated

    @property
    def display_name(self) -> str:
        return self._username

    @property
    def identity(self) -> str:
        return self._email


UserIdT = TypeVar("UserIdT", bound=OptionalUUID)
OrganizationIdT = TypeVar("OrganizationIdT", bound=OptionalUUID)
RolesT = TypeVar("RolesT", bound=OptionalListOfStrings)
ScopesT = TypeVar("ScopesT", bound=OptionalListOfStrings)


class GenericCredentials(
    BaseModel,
    Generic[
        OptionalDomainT,
        UserIdT,
        OrganizationIdT,
        RolesT,
        ScopesT,
    ],
):
    domain: OptionalDomainT = Field(..., description="Domain")
    user_id: UserIdT = Field(..., description="User")
    organization_id: OrganizationIdT = Field(..., description="Organization")
    roles: RolesT = Field(..., description="Roles")
    scopes: ScopesT = Field(..., description="Scopes")


class BaseCredentials(
    GenericCredentials[
        OptionalDomain,
        OptionalUUID,
        OptionalUUID,
        OptionalListOfStrings,
        OptionalListOfStrings,
    ]
):
    domain: Annotated[OptionalDomain, Field(None, description="Domain")] = None
    user_id: Annotated[OptionalUUID, Field(None, description="User")] = None
    organization_id: Annotated[
        OptionalUUID, Field(None, description="Organization")
    ] = None
    roles: Annotated[OptionalListOfStrings, Field(None, description="Roles")] = None
    scopes: Annotated[OptionalListOfStrings, Field(None, description="Scopes")] = None


class AuthenticatedCredentials(
    GenericCredentials[
        Domain,
        UUID,
        OptionalUUID,
        ListOfStrings,
        ListOfStrings,
    ]
):
    domain: Annotated[Domain, Field(..., description="Domain")]
    user_id: Annotated[UUID, Field(..., description="User")]
    organization_id: Annotated[OptionalUUID, Field(..., description="Organization")]
    roles: Annotated[ListOfStrings, Field(..., description="Roles")]
    scopes: Annotated[ListOfStrings, Field(..., description="Scopes")]


class TenantCredentials(
    GenericCredentials[
        Literal[Domain.TENANT],
        UUID,
        UUID,
        ListOfStrings,
        ListOfStrings,
    ]
):
    domain: Literal[Domain.TENANT] = Domain.TENANT
    user_id: Annotated[UUID, Field(..., description="User")]
    organization_id: Annotated[UUID, Field(..., description="Organization")]
    roles: Annotated[ListOfStrings, Field(..., description="Roles")]
    scopes: Annotated[ListOfStrings, Field(..., description="Scopes")]


class SystemCredentials(
    GenericCredentials[
        Literal[Domain.SYSTEM],
        UUID,
        None,
        ListOfStrings,
        ListOfStrings,
    ]
):
    domain: Literal[Domain.SYSTEM] = Domain.SYSTEM
    user_id: Annotated[UUID, Field(..., description="User")]
    organization_id: Annotated[None, Field(None, description="Organization")] = None
    roles: Annotated[ListOfStrings, Field(..., description="Roles")]
    scopes: Annotated[ListOfStrings, Field(..., description="Scopes")]


AnyCredentials = Union[
    BaseCredentials, AuthenticatedCredentials, TenantCredentials, SystemCredentials
]
AnyCredentialsT = TypeVar("AnyCredentialsT", bound=AnyCredentials)


class CredentialsMixin(BaseModel, Generic[AnyCredentialsT]):
    credentials: AnyCredentialsT = Field(..., description="Credentials")


IsAuthenticatedT = TypeVar("IsAuthenticatedT", bound=bool)


class GenericUser(BaseModel, Generic[IsAuthenticatedT]):
    is_authenticated: IsAuthenticatedT = Field(..., description="Authenticated")
    display_name: Annotated[str, Field("", description="Username")] = ""
    identity: Annotated[str, Field("", description="Email")] = ""


class BaseUser(GenericUser[bool]):
    is_authenticated: Annotated[bool, Field(False, description="Authenticated")] = False


class AuthenticatedUser(GenericUser[Literal[True]]):
    is_authenticated: Literal[True] = True


AnyUser = Union[BaseUser, AuthenticatedUser]
AnyUserT = TypeVar("AnyUserT", bound=AnyUser)


class UserMixin(BaseModel, Generic[AnyUserT]):
    user: AnyUserT = Field(..., description="User")


class GenericAuthentication(
    UserMixin[AnyUserT],
    CredentialsMixin[AnyCredentialsT],
    Generic[AnyCredentialsT, AnyUserT],
    ABC,
):
    @classmethod
    def _validate_request_credentials(cls, conn: HTTPConnection):
        if not isinstance(conn.auth, RequestCredentials):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid type of request's credentials: '{type(conn.auth)}'",
            )

    @classmethod
    def _validate_request_user(cls, conn: HTTPConnection):
        if not isinstance(conn.user, RequestUser):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid type of request's user: '{type(conn.user)}'",
            )

    @classmethod
    @abstractmethod
    def _extract(
        cls,
        conn: HTTPConnection,
        /,
    ) -> Self:
        """Main extractor logic"""

    @classmethod
    def extract(
        cls,
        conn: HTTPConnection,
        /,
    ) -> Self:
        try:
            return cls._extract(conn)
        except ValidationError as ve:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ve.errors(),
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "exc_type": type(e).__name__,
                    "exc_data": {
                        "message": str(e),
                        "args": e.args,
                    },
                },
            )

    @classmethod
    def as_dependency(cls) -> Callable[[HTTPConnection], Self]:
        """Create a FastAPI dependency for this authentication"""

        def dependency(conn: HTTPConnection) -> Self:
            return cls.extract(conn)

        return dependency


class BaseAuthentication(GenericAuthentication[BaseCredentials, BaseUser]):
    credentials: Annotated[
        BaseCredentials,
        Field(default_factory=BaseCredentials, description="Credentials"),
    ] = BaseCredentials()

    user: Annotated[BaseUser, Field(default_factory=BaseUser, description="User")] = (
        BaseUser()
    )

    @classmethod
    def _extract(
        cls,
        conn: HTTPConnection,
        /,
    ) -> Self:
        # validate credentials
        cls._validate_request_credentials(conn=conn)
        credentials = BaseCredentials.model_validate(conn.auth, from_attributes=True)

        # validate user
        cls._validate_request_user(conn=conn)
        user = BaseUser.model_validate(conn.user, from_attributes=True)
        return cls(credentials=credentials, user=user)


class AuthenticatedAuthentication(
    GenericAuthentication[AuthenticatedCredentials, AuthenticatedUser]
):
    credentials: Annotated[
        AuthenticatedCredentials, Field(..., description="Credentials")
    ]

    user: Annotated[
        AuthenticatedUser, Field(default_factory=AuthenticatedUser, description="User")
    ] = AuthenticatedUser()

    @classmethod
    def _extract(
        cls,
        conn: HTTPConnection,
        /,
    ) -> Self:
        # validate credentials
        cls._validate_request_credentials(conn=conn)
        credentials = AuthenticatedCredentials.model_validate(
            conn.auth, from_attributes=True
        )

        # validate user
        cls._validate_request_user(conn=conn)
        user = AuthenticatedUser.model_validate(conn.user, from_attributes=True)
        return cls(credentials=credentials, user=user)


class TenantAuthentication(GenericAuthentication[TenantCredentials, AuthenticatedUser]):
    credentials: Annotated[TenantCredentials, Field(..., description="Credentials")]

    user: Annotated[
        AuthenticatedUser, Field(default_factory=AuthenticatedUser, description="User")
    ] = AuthenticatedUser()

    @classmethod
    def _extract(
        cls,
        conn: HTTPConnection,
        /,
    ) -> Self:
        # validate credentials
        cls._validate_request_credentials(conn=conn)
        credentials = TenantCredentials.model_validate(conn.auth, from_attributes=True)

        # validate user
        cls._validate_request_user(conn=conn)
        user = AuthenticatedUser.model_validate(conn.user, from_attributes=True)
        return cls(credentials=credentials, user=user)


class SystemAuthentication(GenericAuthentication[SystemCredentials, AuthenticatedUser]):
    credentials: Annotated[SystemCredentials, Field(..., description="Credentials")]

    user: Annotated[
        AuthenticatedUser, Field(default_factory=AuthenticatedUser, description="User")
    ] = AuthenticatedUser()

    @classmethod
    def _extract(
        cls,
        conn: HTTPConnection,
        /,
    ) -> Self:
        # validate credentials
        cls._validate_request_credentials(conn=conn)
        credentials = SystemCredentials.model_validate(conn.auth, from_attributes=True)

        # validate user
        cls._validate_request_user(conn=conn)
        user = AuthenticatedUser.model_validate(conn.user, from_attributes=True)
        return cls(credentials=credentials, user=user)


AnyAuthenticatedAuthentication = Union[
    AuthenticatedAuthentication, TenantAuthentication, SystemAuthentication
]
AnyAuthenticatedAuthenticationT = TypeVar(
    "AnyAuthenticatedAuthenticationT", bound=AnyAuthenticatedAuthentication
)
OptionalAnyAuthenticatedAuthentication = Optional[AnyAuthenticatedAuthentication]
OptionalAnyAuthenticatedAuthenticationT = TypeVar(
    "OptionalAnyAuthenticatedAuthenticationT",
    bound=OptionalAnyAuthenticatedAuthentication,
)


AnyAuthentication = Union[BaseAuthentication, AnyAuthenticatedAuthentication]
AnyAuthenticationT = TypeVar("AnyAuthenticationT", bound=AnyAuthentication)
OptionalAnyAuthentication = Optional[AnyAuthentication]
OptionalAnyAuthenticationT = TypeVar(
    "OptionalAnyAuthenticationT", bound=OptionalAnyAuthentication
)


def is_authenticated(
    authentication: AnyAuthentication,
) -> TypeGuard[AnyAuthenticatedAuthentication]:
    return (
        authentication.user.is_authenticated
        and authentication.credentials.domain is not None
        and authentication.credentials.user_id is not None
        and authentication.credentials.roles is not None
        and authentication.credentials.scopes is not None
    )


def is_tenant(
    authentication: AnyAuthentication,
) -> TypeGuard[TenantAuthentication]:
    return (
        authentication.user.is_authenticated
        and authentication.credentials.domain is Domain.TENANT
        and authentication.credentials.user_id is not None
        and authentication.credentials.organization_id is not None
        and authentication.credentials.roles is not None
        and authentication.credentials.scopes is not None
    )


def is_system(
    authentication: AnyAuthentication,
) -> TypeGuard[SystemAuthentication]:
    return (
        authentication.user.is_authenticated
        and authentication.credentials.domain is Domain.SYSTEM
        and authentication.credentials.user_id is not None
        and authentication.credentials.organization_id is None
        and authentication.credentials.roles is not None
        and authentication.credentials.scopes is not None
    )


class AuthenticationMixin(BaseModel, Generic[OptionalAnyAuthenticationT]):
    authentication: OptionalAnyAuthenticationT = Field(
        ..., description="Authentication"
    )


class Factory:
    @overload
    @classmethod
    def extract(
        cls,
        domain: Literal[Domain.TENANT],
        *,
        conn: HTTPConnection,
        mandatory: Literal[True] = True,
    ) -> TenantAuthentication: ...
    @overload
    @classmethod
    def extract(
        cls,
        domain: Literal[Domain.SYSTEM],
        *,
        conn: HTTPConnection,
        mandatory: Literal[True] = True,
    ) -> SystemAuthentication: ...
    @overload
    @classmethod
    def extract(
        cls,
        domain: None = None,
        *,
        conn: HTTPConnection,
        mandatory: Literal[True] = True,
    ) -> AuthenticatedAuthentication: ...
    @overload
    @classmethod
    def extract(
        cls, domain: None = None, *, conn: HTTPConnection, mandatory: Literal[False]
    ) -> BaseAuthentication: ...
    @overload
    @classmethod
    def extract(
        cls,
        domain: OptionalDomain = None,
        *,
        conn: HTTPConnection,
        mandatory: bool = False,
    ) -> AnyAuthentication: ...
    @classmethod
    def extract(
        cls,
        domain: OptionalDomain = None,
        *,
        conn: HTTPConnection,
        mandatory: bool = True,
    ) -> AnyAuthentication:
        if not mandatory:
            return BaseAuthentication.extract(conn)
        if domain is None:
            return AuthenticatedAuthentication.extract(conn)
        elif domain is Domain.TENANT:
            return TenantAuthentication.extract(conn)
        elif domain is Domain.SYSTEM:
            return SystemAuthentication.extract(conn)

    @overload
    @classmethod
    def as_dependency(
        cls, domain: Literal[Domain.TENANT], *, mandatory: Literal[True] = True
    ) -> Callable[[HTTPConnection], TenantAuthentication]: ...
    @overload
    @classmethod
    def as_dependency(
        cls, domain: Literal[Domain.SYSTEM], *, mandatory: Literal[True] = True
    ) -> Callable[[HTTPConnection], SystemAuthentication]: ...
    @overload
    @classmethod
    def as_dependency(
        cls, domain: None = None, *, mandatory: Literal[True] = True
    ) -> Callable[[HTTPConnection], AuthenticatedAuthentication]: ...
    @overload
    @classmethod
    def as_dependency(
        cls, domain: None = None, *, mandatory: Literal[False]
    ) -> Callable[[HTTPConnection], BaseAuthentication]: ...
    @classmethod
    def as_dependency(
        cls, domain: OptionalDomain = None, *, mandatory: bool = True
    ) -> Callable[[HTTPConnection], AnyAuthentication]:

        def dependency(conn: HTTPConnection) -> AnyAuthentication:
            return cls.extract(domain, conn=conn, mandatory=mandatory)

        return dependency

    @overload
    @classmethod
    def convert(
        cls,
        destination: Literal[ConversionDestination.BASE],
        *,
        authentication: AnyAuthentication,
    ) -> BaseAuthentication: ...
    @overload
    @classmethod
    def convert(
        cls,
        destination: Literal[ConversionDestination.AUTHENTICATED],
        *,
        authentication: AnyAuthentication,
    ) -> AuthenticatedAuthentication: ...
    @overload
    @classmethod
    def convert(
        cls,
        destination: Literal[ConversionDestination.TENANT],
        *,
        authentication: AnyAuthentication,
    ) -> TenantAuthentication: ...
    @overload
    @classmethod
    def convert(
        cls,
        destination: Literal[ConversionDestination.SYSTEM],
        *,
        authentication: AnyAuthentication,
    ) -> BaseAuthentication: ...
    @classmethod
    def convert(
        cls, destination: ConversionDestination, *, authentication: AnyAuthentication
    ) -> AnyAuthentication:
        if destination is ConversionDestination.BASE:
            return BaseAuthentication.model_validate(authentication.model_dump())
        elif destination is ConversionDestination.AUTHENTICATED:
            return AuthenticatedAuthentication.model_validate(
                authentication.model_dump()
            )
        elif destination is ConversionDestination.TENANT:
            if isinstance(authentication, SystemAuthentication):
                raise TypeError(
                    "Failed converting SystemAuthentication to TenantAuthentication",
                    "Both authentications can not be converted into one another",
                )
            return TenantAuthentication.model_validate(authentication.model_dump())
        elif destination is ConversionDestination.SYSTEM:
            if isinstance(authentication, TenantAuthentication):
                raise TypeError(
                    "Failed converting TenantAuthentication to SystemAuthentication",
                    "Both authentications can not be converted into one another",
                )
            return SystemAuthentication.model_validate(authentication.model_dump())
