from functools import cached_property
import os
from dotenv import load_dotenv
from enum import StrEnum
from pathlib import Path
from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings
from typing import Annotated, Optional, Self, TypeVar
from uuid import UUID
from maleo.enums.environment import Environment
from maleo.enums.service import Key, Name
from maleo.types.string import ListOfStrings, OptionalString
from .security.api_key import validate
from .security.authorization import APIKeyAuthorization


class Execution(StrEnum):
    CONTAINER = "container"
    DIRECT = "direct"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


class ApplicationContext(BaseModel):
    environment: Annotated[
        Environment, Field(..., description="Application's environment")
    ]
    key: Annotated[Key, Field(..., description="Application's key")]

    @classmethod
    def from_env(cls) -> "ApplicationContext":
        load_dotenv()
        environment = os.getenv("ENVIRONMENT", None)
        if environment is None:
            raise ValueError("Variable 'ENVIRONMENT' not found in ENV")

        key = os.getenv("SERVICE_KEY", None)
        if key is None:
            raise ValueError("Variable 'SERVICE_KEY' not found in ENV")

        return cls(environment=Environment(environment), key=Key(key))

    @classmethod
    def from_settings(cls, settings: "ApplicationSettings") -> "ApplicationContext":
        return cls(environment=settings.ENVIRONMENT, key=settings.SERVICE_KEY)


OptionalApplicationContext = Optional[ApplicationContext]


class ApplicationContextMixin(BaseModel):
    application_context: Annotated[
        ApplicationContext,
        Field(
            default_factory=ApplicationContext.from_env,
            description="Application's context",
        ),
    ] = ApplicationContext.from_env()


class ApplicationSettings(BaseSettings):
    # Service related settings
    ENVIRONMENT: Annotated[Environment, Field(..., description="Environment")]
    SERVICE_KEY: Annotated[Key, Field(..., description="Application's key")]
    SERVICE_NAME: Annotated[Name, Field(..., description="Application's name")]

    @cached_property
    def context(self) -> ApplicationContext:
        return ApplicationContext(environment=self.ENVIRONMENT, key=self.SERVICE_KEY)

    CLIENT_ID: Annotated[UUID, Field(..., description="Client's ID")]
    CLIENT_SECRET: Annotated[UUID, Field(..., description="Client's Secret")]

    # Serving related settings
    EXECUTION: Annotated[
        Execution, Field(Execution.CONTAINER, description="Execution mode")
    ] = Execution.CONTAINER
    HOST: Annotated[str, Field("127.0.0.1", description="Application's host")] = (
        "127.0.0.1"
    )
    PORT: Annotated[int, Field(8000, description="Application's port")] = 8000
    HOST_PORT: Annotated[int, Field(8000, description="Host's port")] = 8000
    DOCKER_NETWORK: Annotated[
        str, Field("maleo-suite", description="Docker's network")
    ] = "maleo-suite"
    ROOT_PATH: Annotated[str, Field("", description="Application's root path")] = ""

    # Configuration related settings
    USE_LOCAL_CONFIG: Annotated[
        bool, Field(False, description="Whether to use locally stored config")
    ] = False
    CONFIG_PATH: Annotated[OptionalString, Field(None, description="Config path")] = (
        None
    )

    @model_validator(mode="after")
    def validate_config_path(self) -> Self:
        if self.USE_LOCAL_CONFIG:
            if self.CONFIG_PATH is None:
                self.CONFIG_PATH = (
                    f"/etc/maleo/config/{self.SERVICE_KEY}/{self.ENVIRONMENT}.yaml"
                )
            config_path = Path(self.CONFIG_PATH)
            if not config_path.exists() or not config_path.is_file():
                raise ValueError(
                    f"Config path '{self.CONFIG_PATH}' either did not exist or is not a file"
                )

        return self

    # Credential related settings
    GOOGLE_APPLICATION_CREDENTIALS: Annotated[
        str,
        Field(
            "/etc/maleo/credentials/google-service-account.json",
            description="Google application credential's file path",
        ),
    ] = "/etc/maleo/credentials/google-service-account.json"

    # Key related settings
    USE_LOCAL_KEY: Annotated[
        bool, Field(False, description="Whether to use locally stored key")
    ] = False
    PRIVATE_KEY_PASSWORD: Annotated[
        OptionalString, Field(None, description="Private key's password")
    ] = None
    PRIVATE_KEY_PATH: Annotated[
        str, Field("/etc/maleo/keys/private.pem", description="Private key's path")
    ] = "/etc/maleo/keys/private.pem"
    PUBLIC_KEY_PATH: Annotated[
        str, Field("/etc/maleo/keys/public.pem", description="Public key's path")
    ] = "/etc/maleo/keys/public.pem"

    @model_validator(mode="after")
    def validate_keys_path(self) -> Self:
        if self.USE_LOCAL_KEY:
            private_key_path = Path(self.PRIVATE_KEY_PATH)
            if not private_key_path.exists() or not private_key_path.is_file():
                raise ValueError(
                    f"Private key path: '{self.PRIVATE_KEY_PATH}' either did not exist or is not a file"
                )

            public_key_path = Path(self.PUBLIC_KEY_PATH)
            if not public_key_path.exists() or not public_key_path.is_file():
                raise ValueError(
                    f"Public key path: '{self.PUBLIC_KEY_PATH}' either did not exist or is not a file"
                )

        return self

    # Security related settings
    API_KEY: Annotated[str, Field(..., description="Maleo's API Key")]

    @model_validator(mode="after")
    def validate_api_key(self) -> Self:
        validate(self.API_KEY, self.ENVIRONMENT)
        return self

    @cached_property
    def authorization(self) -> APIKeyAuthorization:
        return APIKeyAuthorization(credentials=self.API_KEY)


ApplicationSettingsT = TypeVar("ApplicationSettingsT", bound=ApplicationSettings)
