from fastapi.requests import HTTPConnection
from pydantic import BaseModel, Field
from typing import (
    Annotated,
    Callable,
    Generic,
    Literal,
    Optional,
    TypeGuard,
    TypeVar,
    Union,
    overload,
)
from .authentication import (
    BaseAuthentication,
    TenantAuthentication,
    SystemAuthentication,
    AnyAuthentication,
    AnyAuthenticationT,
    is_authenticated,
    is_tenant as is_tenant_authentication,
    is_system as is_system_authentication,
    AuthenticationMixin,
    Factory as AuthenticationFactory,
)
from .authorization import (
    AnyAuthorization,
    OptionalAnyAuthorization,
    OptionalAnyAuthorizationT,
    AuthorizationMixin,
    Factory as AuthorizationFactory,
)
from .enums import Domain, OptionalDomain, OptionalDomainT, DomainMixin
from .impersonation import (
    Impersonation,
    OptionalImpersonation,
    OptionalImpersonationT,
    ImpersonationMixin,
)


class GenericSecurity(
    ImpersonationMixin[OptionalImpersonationT],
    AuthenticationMixin[AnyAuthenticationT],
    AuthorizationMixin[OptionalAnyAuthorizationT],
    DomainMixin[OptionalDomainT],
    Generic[
        OptionalDomainT,
        OptionalAnyAuthorizationT,
        AnyAuthenticationT,
        OptionalImpersonationT,
    ],
):
    pass


class BaseSecurity(
    GenericSecurity[
        OptionalDomain,
        OptionalAnyAuthorization,
        AnyAuthentication,
        OptionalImpersonation,
    ]
):
    domain: Annotated[OptionalDomain, Field(None, description="Domain")] = None
    authorization: Annotated[
        OptionalAnyAuthorization, Field(None, description="Authorization")
    ] = None
    authentication: Annotated[
        AnyAuthentication,
        Field(default_factory=BaseAuthentication, description="Authentication"),
    ] = BaseAuthentication()
    impersonation: Annotated[
        OptionalImpersonation, Field(None, description="Impersonation")
    ] = None


class TenantSecurity(
    GenericSecurity[
        Literal[Domain.TENANT],
        AnyAuthorization,
        TenantAuthentication,
        OptionalImpersonation,
    ]
):
    domain: Annotated[
        Literal[Domain.TENANT], Field(Domain.TENANT, description="Domain")
    ] = Domain.TENANT
    authorization: Annotated[AnyAuthorization, Field(..., description="Authorization")]
    authentication: Annotated[
        TenantAuthentication, Field(..., description="Authentication")
    ]
    impersonation: Annotated[
        OptionalImpersonation, Field(None, description="Impersonation")
    ] = None


class SystemSecurity(
    GenericSecurity[
        Literal[Domain.SYSTEM],
        AnyAuthorization,
        SystemAuthentication,
        OptionalImpersonation,
    ]
):
    domain: Annotated[
        Literal[Domain.SYSTEM], Field(Domain.SYSTEM, description="Domain")
    ] = Domain.SYSTEM
    authorization: Annotated[AnyAuthorization, Field(..., description="Authorization")]
    authentication: Annotated[
        SystemAuthentication, Field(..., description="Authentication")
    ]
    impersonation: Annotated[
        OptionalImpersonation, Field(None, description="Impersonation")
    ] = None


SecuredSecurity = Union[TenantSecurity, SystemSecurity]
SecuredSecurityT = TypeVar("SecuredSecurityT", bound=SecuredSecurity)
OptionalSecuredSecurity = Optional[SecuredSecurity]
OptionalSecuredSecurityT = TypeVar(
    "OptionalSecuredSecurityT", bound=OptionalSecuredSecurity
)


AnySecurity = Union[BaseSecurity, SecuredSecurity]
AnySecurityT = TypeVar("AnySecurityT", bound=AnySecurity)
OptionalAnySecurity = Optional[AnySecurity]
OptionalAnySecurityT = TypeVar("OptionalAnySecurityT", bound=OptionalAnySecurity)


def is_secured(
    security: AnySecurity,
) -> TypeGuard[SecuredSecurity]:
    return (
        security.domain is not None
        and security.authorization is not None
        and is_authenticated(security.authentication)
    )


def is_tenant(
    security: AnySecurity,
) -> TypeGuard[TenantAuthentication]:
    return (
        security.domain is not None
        and security.authorization is not None
        and is_tenant_authentication(security.authentication)
    )


def is_system(
    security: AnySecurity,
) -> TypeGuard[SystemAuthentication]:
    return (
        security.domain is not None
        and security.authorization is not None
        and is_system_authentication(security.authentication)
    )


class SecurityMixin(BaseModel, Generic[OptionalAnySecurityT]):
    security: OptionalAnySecurityT = Field(..., description="Security")


class Factory:
    @overload
    @classmethod
    def extract(
        cls,
        domain: Literal[Domain.TENANT],
        *,
        conn: HTTPConnection,
    ) -> TenantSecurity: ...
    @overload
    @classmethod
    def extract(
        cls,
        domain: Literal[Domain.SYSTEM],
        *,
        conn: HTTPConnection,
    ) -> SystemSecurity: ...
    @overload
    @classmethod
    def extract(
        cls,
        domain: Domain,
        *,
        conn: HTTPConnection,
    ) -> SecuredSecurity: ...
    @overload
    @classmethod
    def extract(
        cls,
        domain: None = None,
        *,
        conn: HTTPConnection,
    ) -> BaseSecurity: ...
    @classmethod
    def extract(
        cls,
        domain: OptionalDomain = None,
        *,
        conn: HTTPConnection,
    ) -> AnySecurity:
        impersonation = Impersonation.extract(conn)

        if domain is None:
            return BaseSecurity(
                authorization=AuthorizationFactory.extract(conn=conn, auto_error=False),
                authentication=AuthenticationFactory.extract(conn=conn),
                impersonation=impersonation,
            )
        elif domain is Domain.TENANT:
            return TenantSecurity(
                authorization=AuthorizationFactory.extract(conn=conn, auto_error=True),
                authentication=AuthenticationFactory.extract(domain, conn=conn),
                impersonation=impersonation,
            )
        elif domain is Domain.SYSTEM:
            return SystemSecurity(
                authorization=AuthorizationFactory.extract(conn=conn, auto_error=True),
                authentication=AuthenticationFactory.extract(domain, conn=conn),
                impersonation=impersonation,
            )

    @overload
    @classmethod
    def as_dependency(
        cls,
        domain: Literal[Domain.TENANT],
    ) -> Callable[[HTTPConnection], TenantSecurity]: ...
    @overload
    @classmethod
    def as_dependency(
        cls,
        domain: Literal[Domain.SYSTEM],
    ) -> Callable[[HTTPConnection], SystemSecurity]: ...
    @overload
    @classmethod
    def as_dependency(
        cls,
        domain: Domain,
    ) -> Callable[[HTTPConnection], SecuredSecurity]: ...
    @overload
    @classmethod
    def as_dependency(
        cls,
        domain: None = None,
    ) -> Callable[[HTTPConnection], BaseSecurity]: ...
    @classmethod
    def as_dependency(
        cls,
        domain: OptionalDomain = None,
    ) -> Callable[[HTTPConnection], AnySecurity]:

        def dependency(conn: HTTPConnection) -> AnySecurity:
            return cls.extract(domain, conn=conn)

        return dependency
