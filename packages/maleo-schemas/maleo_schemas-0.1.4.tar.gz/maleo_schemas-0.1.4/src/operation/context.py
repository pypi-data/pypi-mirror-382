from pydantic import BaseModel, Field
from typing import Generic
from maleo.types.dict import OptionalStringToAnyDict
from maleo.types.enum import StringEnumT
from .enums import (
    Origin as OriginEnum,
    Layer as LayerEnum,
    Target as TargetEnum,
)


class Component(BaseModel, Generic[StringEnumT]):
    type: StringEnumT = Field(..., description="Component's type")
    details: OptionalStringToAnyDict = Field(None, description="Component's details")


class Origin(Component[OriginEnum]):
    pass


class OriginMixin(BaseModel):
    origin: Origin = Field(..., description="Operation's origin")


class Layer(Component[LayerEnum]):
    pass


class LayerMixin(BaseModel):
    layer: Layer = Field(..., description="Operation's layer")


class Target(Component[TargetEnum]):
    pass


class TargetMixin(BaseModel):
    target: Target = Field(..., description="Operation's target")


class Context(TargetMixin, LayerMixin, OriginMixin):
    pass


class ContextMixin(BaseModel):
    context: Context = Field(..., description="Operation's context")


UTILITY_OPERATION_CONTEXT = Context(
    origin=Origin(type=OriginEnum.UTILITY, details=None),
    layer=Layer(type=LayerEnum.INTERNAL, details=None),
    target=Target(type=TargetEnum.INTERNAL, details=None),
)


def generate(
    origin: OriginEnum,
    layer: LayerEnum,
    target: TargetEnum = TargetEnum.INTERNAL,
    origin_details: OptionalStringToAnyDict = None,
    layer_details: OptionalStringToAnyDict = None,
    target_details: OptionalStringToAnyDict = None,
) -> Context:
    return Context(
        origin=Origin(type=origin, details=origin_details),
        layer=Layer(type=layer, details=layer_details),
        target=Target(type=target, details=target_details),
    )
