from collections.abc import Iterable, Sequence
from Crypto.PublicKey.RSA import RsaKey
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field, ValidationError, model_validator
from typing import (
    Annotated,
    Generic,
    Literal,
    Optional,
    Self,
    Tuple,
    TypeGuard,
    TypeVar,
    Union,
    overload,
)
from uuid import UUID
from maleo.crypto.token import decode, encode
from maleo.enums.expiration import Expiration
from maleo.types.datetime import OptionalDatetime
from maleo.types.integer import OptionalInteger
from maleo.types.misc import BytesOrString
from maleo.types.string import ListOfStrings, OptionalListOfStrings, OptionalString
from maleo.types.uuid import OptionalUUID
from .enums import Domain, OptionalDomain, DomainT


class TokenV1(BaseModel):
    iss: Annotated[OptionalString, Field(None, description="Issuer")] = None
    sub: Annotated[str, Field(..., description="Subject")]
    sr: Annotated[str, Field(..., description="System role")]
    u_i: Annotated[int, Field(..., description="User's ID")]
    u_uu: Annotated[UUID, Field(..., description="User's UUID")]
    u_u: Annotated[str, Field(..., description="User's Username")]
    u_e: Annotated[str, Field(..., description="User's Email")]
    u_ut: Annotated[str, Field(..., description="User's type")]
    o_i: Annotated[OptionalInteger, Field(None, description="Organization's ID")] = None
    o_uu: Annotated[OptionalUUID, Field(None, description="Organization's UUID")] = None
    o_k: Annotated[OptionalString, Field(None, description="Organization's Key")] = None
    o_ot: Annotated[OptionalString, Field(None, description="Organization's type")] = (
        None
    )
    uor: Annotated[
        OptionalListOfStrings,
        Field(None, description="Organization's type", min_length=1),
    ] = None
    iat_dt: Annotated[datetime, Field(..., description="Issued At Timestamp")]
    iat: Annotated[int, Field(..., description="Issued at")]
    exp_dt: Annotated[datetime, Field(..., description="Expired At Timestamp")]
    exp: Annotated[int, Field(..., description="Expired at")]

    @classmethod
    def from_string(
        cls,
        token: str,
        *,
        key: Union[RsaKey, BytesOrString],
        audience: str | Iterable[str] | None = None,
        subject: OptionalString = None,
        issuer: str | Sequence[str] | None = None,
        leeway: float | timedelta = 0,
    ) -> "TokenV1":
        obj = decode(
            token,
            key=key,
            audience=audience,
            subject=subject,
            issuer=issuer,
            leeway=leeway,
        )
        return cls.model_validate(obj)


class Claim(BaseModel):
    iss: Annotated[OptionalString, Field(None, description="Issuer")] = None
    sub: Annotated[UUID, Field(..., description="Subject")]
    aud: Annotated[OptionalString, Field(None, description="Audience")] = None
    exp: Annotated[int, Field(..., description="Expired at")]
    iat: Annotated[int, Field(..., description="Issued at")]

    @classmethod
    def new_timestamp(
        cls, iat_dt: OptionalDatetime = None, exp_in: Expiration = Expiration.EXP_15MN
    ) -> Tuple[int, int]:
        if iat_dt is None:
            iat_dt = datetime.now(tz=timezone.utc)
        exp_dt = iat_dt + timedelta(seconds=exp_in.value)
        return int(iat_dt.timestamp()), int(exp_dt.timestamp())


OrganizationT = TypeVar("OrganizationT", bound=OptionalUUID)


class Credential(BaseModel, Generic[DomainT, OrganizationT]):
    d: DomainT = Field(..., description="Domain")
    o: OrganizationT = Field(..., description="Organization")
    r: Annotated[ListOfStrings, Field(..., min_length=1, description="Roles")]


class GenericToken(
    Credential[DomainT, OrganizationT],
    Claim,
    Generic[DomainT, OrganizationT],
):
    @classmethod
    def from_string(
        cls,
        token: str,
        *,
        key: Union[RsaKey, BytesOrString],
        audience: str | Iterable[str] | None = None,
        subject: OptionalString = None,
        issuer: str | Sequence[str] | None = None,
        leeway: float | timedelta = 0,
    ) -> Self:
        obj = decode(
            token,
            key=key,
            audience=audience,
            subject=subject,
            issuer=issuer,
            leeway=leeway,
        )
        return cls.model_validate(obj)

    @property
    def scopes(self) -> ListOfStrings:
        return [f"{str(self.d)}:{str(r)}" for r in self.r]

    @model_validator(mode="after")
    def validate_credential(self) -> Self:
        return self

    @overload
    def to_string(
        self,
        key: RsaKey,
    ) -> str: ...
    @overload
    def to_string(
        self,
        key: BytesOrString,
        *,
        password: OptionalString = None,
    ) -> str: ...
    def to_string(
        self,
        key: Union[RsaKey, BytesOrString],
        *,
        password: OptionalString = None,
    ) -> str:
        if isinstance(key, RsaKey):
            return encode(
                payload=self.model_dump(mode="json", exclude_none=True),
                key=key,
            )
        else:
            return encode(
                payload=self.model_dump(mode="json", exclude_none=True),
                key=key,
                password=password,
            )


class TenantToken(GenericToken[Literal[Domain.TENANT], UUID]):
    d: Annotated[Literal[Domain.TENANT], Field(Domain.TENANT, description="Domain")] = (
        Domain.TENANT
    )

    @model_validator(mode="after")
    def validate_identity(self) -> Self:
        if self.d is not Domain.TENANT:
            raise ValueError(f"Value of 'd' claim must be {Domain.TENANT}")
        if not isinstance(self.o, UUID):
            raise ValueError(f"Value of 'o' claim must be an UUID. Value: {self.o}")
        return self

    @classmethod
    def new(
        cls,
        *,
        sub: UUID,
        o: UUID,
        r: ListOfStrings,
        iss: OptionalString = None,
        aud: OptionalString = None,
        iat_dt: OptionalDatetime = None,
        exp_in: Expiration = Expiration.EXP_15MN,
    ) -> "TenantToken":
        iat, exp = cls.new_timestamp(iat_dt, exp_in)
        return cls(iss=iss, sub=sub, aud=aud, exp=exp, iat=iat, o=o, r=r)


class SystemToken(GenericToken[Literal[Domain.SYSTEM], None]):
    d: Annotated[Literal[Domain.SYSTEM], Field(Domain.SYSTEM, description="Domain")] = (
        Domain.SYSTEM
    )
    o: None = None

    @model_validator(mode="after")
    def validate_identity(self) -> Self:
        if self.d is not Domain.SYSTEM:
            raise ValueError(f"Value of 'd' claim must be {Domain.SYSTEM}")
        if self.o is not None:
            raise ValueError(f"Value of 'o' claim must be None. Value: {self.o}")
        return self

    @classmethod
    def new(
        cls,
        *,
        sub: UUID,
        r: ListOfStrings,
        iss: OptionalString = None,
        aud: OptionalString = None,
        iat_dt: OptionalDatetime = None,
        exp_in: Expiration = Expiration.EXP_15MN,
    ) -> "SystemToken":
        iat, exp = cls.new_timestamp(iat_dt, exp_in)
        return cls(iss=iss, sub=sub, aud=aud, exp=exp, iat=iat, r=r)


AnyToken = Union[TenantToken, SystemToken]
AnyTokenT = TypeVar("AnyTokenT", bound=AnyToken)
OptionalAnyToken = Optional[AnyToken]
OptionalAnyTokenT = TypeVar("OptionalAnyTokenT", bound=OptionalAnyToken)


class TokenMixin(BaseModel, Generic[OptionalAnyTokenT]):
    token: OptionalAnyTokenT = Field(..., description="Token")


def is_tenant(token: AnyToken) -> TypeGuard[TenantToken]:
    return (
        isinstance(token, TenantToken)
        and token.d is Domain.TENANT
        and token.o is not None
    )


def is_system(token: AnyToken) -> TypeGuard[SystemToken]:
    return (
        isinstance(token, SystemToken) and token.d is Domain.SYSTEM and token.o is None
    )


class Factory:
    @overload
    @staticmethod
    def from_string(
        token: str,
        domain: Literal[Domain.TENANT],
        *,
        key: Union[RsaKey, BytesOrString],
        audience: str | Iterable[str] | None = None,
        subject: OptionalString = None,
        issuer: str | Sequence[str] | None = None,
        leeway: float | timedelta = 0,
    ) -> TenantToken: ...
    @overload
    @staticmethod
    def from_string(
        token: str,
        domain: Literal[Domain.SYSTEM],
        *,
        key: Union[RsaKey, BytesOrString],
        audience: str | Iterable[str] | None = None,
        subject: OptionalString = None,
        issuer: str | Sequence[str] | None = None,
        leeway: float | timedelta = 0,
    ) -> SystemToken: ...
    @overload
    @staticmethod
    def from_string(
        token: str,
        domain: None = None,
        *,
        key: Union[RsaKey, BytesOrString],
        audience: str | Iterable[str] | None = None,
        subject: OptionalString = None,
        issuer: str | Sequence[str] | None = None,
        leeway: float | timedelta = 0,
    ) -> AnyToken: ...
    @staticmethod
    def from_string(
        token: str,
        domain: OptionalDomain = None,
        *,
        key: Union[RsaKey, BytesOrString],
        audience: str | Iterable[str] | None = None,
        subject: OptionalString = None,
        issuer: str | Sequence[str] | None = None,
        leeway: float | timedelta = 0,
    ) -> AnyToken:
        validated_token = None
        models = (TokenV1, TenantToken, SystemToken)
        for model in models:
            try:
                validated_token = model.from_string(
                    token,
                    key=key,
                    audience=audience,
                    subject=subject,
                    issuer=issuer,
                    leeway=leeway,
                )
            except ValidationError:
                continue
        if validated_token is None:
            raise ValueError("Unable to validate raw token into known token model")

        if isinstance(validated_token, (TenantToken, SystemToken)):
            result_token = validated_token
        else:
            if validated_token.sr == "administrator":
                if (
                    validated_token.o_i is not None
                    or validated_token.o_uu is not None
                    or validated_token.o_k is not None
                    or validated_token.o_ot is not None
                    or validated_token.uor is not None
                ):
                    raise ValueError(
                        "All organization-related claims must be None for System token"
                    )
                result_token = SystemToken(
                    iss=validated_token.iss,
                    sub=validated_token.u_uu,
                    aud=None,
                    exp=validated_token.exp,
                    iat=validated_token.iat,
                    r=["administrator", "user"],
                )
            elif validated_token.sr == "user":
                if (
                    validated_token.o_i is None
                    or validated_token.o_uu is None
                    or validated_token.o_k is None
                    or validated_token.o_ot is None
                    or validated_token.uor is None
                ):
                    raise ValueError(
                        "All organization-related claims can not be None for Tenant Token"
                    )
                result_token = TenantToken(
                    iss=validated_token.iss,
                    sub=validated_token.u_uu,
                    aud=None,
                    exp=validated_token.exp,
                    iat=validated_token.iat,
                    o=validated_token.o_uu,
                    r=validated_token.uor,
                )
            else:
                raise ValueError(
                    f"Claim 'sr' can only be either 'administrator' or 'user' but received {validated_token.sr}"
                )

        if domain is None:
            return result_token
        elif domain is Domain.TENANT:
            if not is_tenant(result_token):
                raise ValueError(
                    "Failed parsing Tenant Token from string, raw token did not qualify as Tenant Token"
                )
            return result_token
        elif domain is Domain.SYSTEM:
            if not is_system(result_token):
                raise ValueError(
                    "Failed parsing System token from string, raw token did not qualify as System Token"
                )
            return result_token
