from pydantic import BaseModel, Field
from typing import Dict, Generic, Optional, TypeVar, Union
from .mixins.general import Success, Descriptor, Other


AnyMetadataT = TypeVar("AnyMetadataT")
ModelMetadataT = TypeVar("ModelMetadataT", bound=Optional[BaseModel])


class MetadataMixin(BaseModel, Generic[AnyMetadataT]):
    metadata: AnyMetadataT = Field(..., description="Metadata")


class FieldExpansionMetadata(Other, Descriptor[str], Success[bool]):
    pass


class FieldExpansionMetadataMixin(BaseModel):
    field_expansion: Optional[Union[str, Dict[str, FieldExpansionMetadata]]] = Field(
        None, description="Field expansion metadata"
    )
