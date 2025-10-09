from pydantic import BaseModel, Field
from typing import Any
from typing_extensions import Annotated
from maleo.types.string import OptionalListOfStrings


class ErrorMetadata(BaseModel):
    details: Annotated[Any, Field(None, description="Details")] = None
    traceback: Annotated[
        OptionalListOfStrings, Field(None, description="Traceback")
    ] = None


class ErrorMetadataMixin(BaseModel):
    metadata: Annotated[
        ErrorMetadata, Field(ErrorMetadata(), description="Error's Metadata")
    ] = ErrorMetadata()
