"""FDL schema type definitions.

This schema module provides a centralized collection of Pydantic models representing the ASC Framing
Decision List specification for improved maintainability and readability.

All the FDL schema are generated based on the official `ascfdl.schema.v2.json`, but small number of
attribute field settings are slighlty modified to better suit the Python API usage.

Note on underscore-prefixed classes:
Classes that start with an underscore (e.g., `_Canvas`, `_Context`, `_CanvasTemplate`) are base
schema models intended to be inherited and extended in their respective separate modules. These
extensions provide additional convenience methods, custom validations, and enhanced functionality
while maintaining schema compatibility.
"""

from typing import Annotated, Literal, Optional, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict, Field, RootModel
from enum import Enum
from uuid import UUID


if TYPE_CHECKING:
    from .context import Context
    from .canvas import Canvas
    from .template import CanvasTemplate


class Version(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    major: Literal[2] = 2
    minor: Literal[0] = 0


class Sequence(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    value: str
    idx: Annotated[str, Field(max_length=1, min_length=1)]
    min: Annotated[int, Field(ge=0)]
    max: Annotated[int, Field(ge=0)]


class ClipId(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    clip_name: str
    file: Optional[str] = None
    sequence: Optional[Sequence] = None


class FitSource(Enum):
    framing_decision_dimensions = "framing_decision.dimensions"
    framing_decision_protection_dimensions = "framing_decision.protection_dimensions"
    canvas_dimensions = "canvas.dimensions"
    canvas_effective_dimensions = "canvas.effective_dimensions"


class FitMethod(Enum):
    width = "width"
    height = "height"
    fit_all = "fit_all"
    fill = "fill"


class AlignmentMethodVertical(Enum):
    top = "top"
    center = "center"
    bottom = "bottom"


class AlignmentMethodHorizontal(Enum):
    left = "left"
    center = "center"
    right = "right"


class PreserveFromSourceCanvas(Enum):
    none = "none"
    framing_decision_dimensions = "framing_decision.dimensions"
    framing_decision_protection_dimensions = "framing_decision.protection_dimensions"
    canvas_dimensions = "canvas.dimensions"
    canvas_effective_dimensions = "canvas.effective_dimensions"


class Even(Enum):
    whole = "whole"
    even = "even"


class Mode(Enum):
    up = "up"
    down = "down"
    round = "round"


class Round(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    even: Even
    mode: Mode


class FdlId(RootModel[str]):
    root: Annotated[str, Field(max_length=32, min_length=1, pattern="^[A-Za-z0-9_]+$")]

    def __str__(self) -> str:
        return self.root


class FdlIdFramingDecision(RootModel[str]):
    root: Annotated[
        str, Field(max_length=65, min_length=3, pattern="^[A-Za-z0-9_]+-[A-Za-z0-9_]+$")
    ]

    def __str__(self) -> str:
        return self.root


class DimensionsInt(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    width: Annotated[int, Field(ge=0)]
    height: Annotated[int, Field(ge=0)]


class DimensionsFloat(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    width: Annotated[float, Field(ge=0.0)]
    height: Annotated[float, Field(ge=0.0)]


class PointFloat(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    x: float
    y: float


class FramingIntent(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    label: Optional[str] = None
    id: FdlId
    aspect_ratio: DimensionsInt
    protection: Annotated[float, Field(ge=0.0, le=1.0)] = 0.0


class FramingDecision(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    label: Optional[str] = None
    id: FdlIdFramingDecision
    framing_intent_id: FdlId
    dimensions: DimensionsFloat
    anchor_point: PointFloat
    protection_dimensions: Optional[DimensionsFloat] = None
    protection_anchor_point: Optional[PointFloat] = None


class _Canvas(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )
    label: Optional[str] = None
    id: FdlId
    source_canvas_id: FdlId
    dimensions: DimensionsInt
    effective_dimensions: Optional[DimensionsInt] = None
    effective_anchor_point: Optional[PointFloat] = None
    photosite_dimensions: Optional[DimensionsInt] = None
    physical_dimensions: Optional[DimensionsFloat] = None
    anamorphic_squeeze: Annotated[Optional[float], Field(gt=0.0)] = 1.0
    framing_decisions: Optional[list[FramingDecision]] = None


class _Context(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )
    label: Optional[str] = None
    context_creator: Optional[str] = None
    clip_id: Optional[ClipId] = None
    canvases: Optional[list["Canvas"]] = None


class _CanvasTemplate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )
    label: Optional[str] = None
    id: FdlId
    target_dimensions: DimensionsInt
    target_anamorphic_squeeze: Annotated[float, Field(ge=0.0)]
    fit_source: FitSource
    fit_method: FitMethod
    alignment_method_vertical: Optional[AlignmentMethodVertical] = AlignmentMethodVertical.center
    alignment_method_horizontal: Optional[AlignmentMethodHorizontal] = (
        AlignmentMethodHorizontal.center
    )
    preserve_from_source_canvas: Optional[PreserveFromSourceCanvas] = PreserveFromSourceCanvas.none
    maximum_dimensions: Optional[DimensionsInt] = None
    pad_to_maximum: Optional[bool] = False
    round: Optional[Round] = None


class _AscFramingDecisionList(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )
    uuid: Optional[UUID] = None
    version: Optional[Version] = None
    fdl_creator: Optional[str] = None
    default_framing_intent: Optional[FdlId] = None
    framing_intents: Optional[list[FramingIntent]] = None
    contexts: Optional[list["Context"]] = None
    canvas_templates: Optional[list["CanvasTemplate"]] = None
