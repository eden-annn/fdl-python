"""FDL CanvasTemplate Processor module.

Applies a `CanvasTemplate` to a source `Canvas` to produce a derived canvas. The processor runs a
complete pipeline to generate a new Canvas according to the template's rules, which includes:
 - resolves source/target dimensions
 - scale factors
 - handles preserved-source rules
 - enforces maximum/pad constraints,
 - performs rounding
 - rescales framing decisions
"""

from typing import Optional, Union

from .calc import rounding, to_int_dimensions
from .canvas import Canvas
from .template import CanvasTemplate
from .schema import (
    DimensionsInt,
    DimensionsFloat,
    FdlId,
    FitSource,
    PointFloat,
    FramingDecision,
    FitMethod,
    PreserveFromSourceCanvas,
    FdlIdFramingDecision,
)


class CanvasTemplateProcessor:
    """Processor that applies a `CanvasTemplate` to a source `Canvas`.

    The processor is initialized with a `CanvasTemplate`. Calling `create_canvas` with a source
    canvas runs the complete template pipeline, and assembles the resulting `Canvas`.
    """

    def __init__(self, template: CanvasTemplate):
        """Initialize the processor with a `CanvasTemplate`."""
        self.template = template

    def create_canvas(
        self,
        source_canvas: Canvas,
        framing_decision_id: Optional[FdlIdFramingDecision] = None,
        new_canvas_id: Optional[FdlId] = None,
        new_canvas_label: Optional[str] = None,
    ) -> Canvas:
        """Build a new `Canvas` derived from `source_canvas` using the template settings."""
        # Target dimensions and scale
        target_dims, scale = self._get_target_dimensions_and_scale(
            source_canvas, framing_decision_id
        )

        # Preserved dimensions
        preserved_target_dims = self._get_preserved_target_dimensions(
            source_canvas, scale, framing_decision_id
        )

        canvas_target_dims = preserved_target_dims or target_dims

        # Effective dimensions
        effective_dims: Optional[DimensionsFloat] = None
        if (
            self.template.fit_source == FitSource.canvas_dimensions
            or self.template.preserve_from_source_canvas
            == PreserveFromSourceCanvas.canvas_dimensions
        ) and source_canvas.effective_dimensions:
            # If preserve_from_source_canvas is defined as canvas.dimensions in the template, and
            # canvases.effective_dimensions and canvases.effective_anchor_point existed, these must
            # also be respected, re-calculated, and included in the output canvas.
            effective_dims = DimensionsFloat(
                width=source_canvas.effective_dimensions.width * scale,
                height=source_canvas.effective_dimensions.height * scale,
            )
        elif preserved_target_dims and (target_dims.width, target_dims.height) != (
            preserved_target_dims.width,
            preserved_target_dims.height,
        ):
            # If preserve from source canvas is different than fitsource, then the output canvas
            # will be larger than the target dimensions to account for the protected area. In which
            # case, the effective dimensions of the output canvas should reflect the actual active
            # pixels.
            effective_dims = DimensionsFloat(
                width=target_dims.width,
                height=target_dims.height,
            )

        # Maximum dimensions
        canvas_target_dims, effective_dims = self._apply_maximum_dimensions(
            source_canvas, canvas_target_dims, effective_dims
        )

        # Suggest a new canvas ID, "<source canvas ID>_<template ID>", if not already provided
        if not new_canvas_id:
            new_canvas_id = FdlId(f"{str(source_canvas.id)}_{str(self.template.id)}")

        new_framing_decisions = self._get_framing_decisions(source_canvas, scale)

        # Create a new Canvas with the calculated properties
        canvas = Canvas(
            label=new_canvas_label,
            id=new_canvas_id,
            source_canvas_id=source_canvas.id,
            dimensions=self._apply_rounding(canvas_target_dims),
            effective_dimensions=to_int_dimensions(effective_dims) if effective_dims else None,
            anamorphic_squeeze=(
                self.template.target_anamorphic_squeeze or source_canvas.anamorphic_squeeze
            ),
            framing_decisions=new_framing_decisions,
        )

        return canvas

    def _apply_maximum_dimensions(
        self,
        source_canvas: Canvas,
        target_dimensions: DimensionsFloat,
        effective_dimensions: Optional[DimensionsFloat] = None,
    ) -> tuple[DimensionsFloat, Optional[DimensionsFloat]]:
        """Enforce the template's maximum_dimensions and pad_to_maximum behavior.

        When pad_to_maximum is True and the source had no effective_dimensions, this method records
        the active image area as the output effective_dimensions and expands the canvas to the
        template's maximum_dimensions. When pad_to_maximum is False the computed target dimensions
        are cropped to not exceed maximum_dimensions.
        """
        if not self.template.maximum_dimensions:
            return target_dimensions, effective_dimensions

        if self.template.pad_to_maximum:
            if not source_canvas.effective_dimensions and (
                target_dimensions.width < self.template.maximum_dimensions.width
                or target_dimensions.height < self.template.maximum_dimensions.height
            ):
                # If the output canvas includes padding as a result of pad_to_maximum, and the
                # source canvas did not include defined effective_dimensions, the output canvas
                # must specify new effective_dimensions and effective_anchor_point values based
                # on the outer bounds of the active image area within maximum_dimensions.
                effective_dimensions = DimensionsFloat(
                    width=target_dimensions.width,
                    height=target_dimensions.height,
                )
            target_dimensions = DimensionsFloat(
                width=self.template.maximum_dimensions.width,
                height=self.template.maximum_dimensions.height,
            )
        else:
            target_dimensions = DimensionsFloat(
                width=min(target_dimensions.width, self.template.maximum_dimensions.width),
                height=min(target_dimensions.height, self.template.maximum_dimensions.height),
            )

        return target_dimensions, effective_dimensions

    def _apply_rounding(self, dims: DimensionsFloat) -> DimensionsInt:
        """Convert a floating-dimension to integer dimensions according to template's Round setting.

        The Round setting is disregarded if maximum_dimensions and pad_to_maximum are set.
        """
        if (
            self.template.round
            and not self.template.maximum_dimensions
            and not self.template.pad_to_maximum
        ):
            return DimensionsInt(
                width=rounding(dims.width, self.template.round),
                height=rounding(dims.height, self.template.round),
            )

        return to_int_dimensions(dims)

    def _get_framing_decisions(
        self, source_canvas: Canvas, scale_factor: float
    ) -> Optional[list[FramingDecision]]:
        """Get a copy of the original source canvas's framing decisions but are rescaled to fit
        into the template.
        """
        if not source_canvas.framing_decisions:
            return None

        new_framing_decisions: list[FramingDecision] = []
        for framing_decision in source_canvas.framing_decisions:
            # create a deep copy of the framing decision model
            new_fd = framing_decision.model_copy(deep=True)

            # replace numeric submodels with scaled copies
            new_fd.dimensions = DimensionsFloat(
                width=framing_decision.dimensions.width * scale_factor,
                height=framing_decision.dimensions.height * scale_factor,
            )

            new_fd.anchor_point = PointFloat(
                x=framing_decision.anchor_point.x * scale_factor,
                y=framing_decision.anchor_point.y * scale_factor,
            )

            if framing_decision.protection_dimensions:
                new_fd.protection_dimensions = DimensionsFloat(
                    width=framing_decision.protection_dimensions.width * scale_factor,
                    height=framing_decision.protection_dimensions.height * scale_factor,
                )

            if framing_decision.protection_anchor_point:
                new_fd.protection_anchor_point = PointFloat(
                    x=framing_decision.protection_anchor_point.x * scale_factor,
                    y=framing_decision.protection_anchor_point.y * scale_factor,
                )

            new_framing_decisions.append(new_fd)

        return new_framing_decisions

    def _get_preserved_target_dimensions(
        self,
        source_canvas: Canvas,
        scale_factor: float,
        framing_decision_id: Optional[FdlIdFramingDecision] = None,
    ) -> Optional[DimensionsFloat]:
        """Compute the dimensions that must be preserved from the source canvas when the template's
        preserve_from_source_canvas is set.
        """
        if (
            self.template.preserve_from_source_canvas is None
            or self.template.preserve_from_source_canvas == PreserveFromSourceCanvas.none
        ):
            return None

        preserved_source_dims = self._get_source_dims(
            self.template.preserve_from_source_canvas,
            source_canvas,
            framing_decision_id=framing_decision_id,
        )
        desqueezed_preserved_source_dims = self._get_anamorphic_desqueezed_dimensions(
            source_canvas, preserved_source_dims
        )

        preserved_target_dims = DimensionsFloat(
            width=desqueezed_preserved_source_dims.width * scale_factor,
            height=desqueezed_preserved_source_dims.height * scale_factor,
        )

        return preserved_target_dims

    def _get_source_dims(
        self,
        source: Union[FitSource, PreserveFromSourceCanvas],
        source_canvas: Canvas,
        framing_decision_id: Optional[FdlIdFramingDecision] = None,
    ) -> DimensionsFloat:
        """Resolve the source dimensions according to the `source` selector.

        When framing-decision-based values are used, `framing_decision_id` must be provided and the
        corresponding framing decision must be located on the source canvas.
        """
        # FitSource: framing_decision.dimensions or protection_dimensions
        if source in (
            FitSource.framing_decision_dimensions,
            FitSource.framing_decision_protection_dimensions,
            PreserveFromSourceCanvas.framing_decision_dimensions,
            PreserveFromSourceCanvas.framing_decision_protection_dimensions,
        ):
            if not framing_decision_id:
                raise ValueError(
                    "`framing_decision_id` must be provided when using "
                    "framing_decision as fit_source or preserve_from_source_canvas"
                )

            if source_canvas.framing_decisions is None:
                raise ValueError(
                    f"Framing decisions are not found from the canvas: {source_canvas.id}"
                )

            for fd in source_canvas.framing_decisions:
                if fd.id == framing_decision_id:
                    framing_decision = fd
                    break
            else:
                raise ValueError(
                    f"Framing decision ID {framing_decision_id} not found "
                    f"in canvas {source_canvas.id}"
                )

            if framing_decision.protection_dimensions and source in (
                FitSource.framing_decision_protection_dimensions,
                PreserveFromSourceCanvas.framing_decision_protection_dimensions,
            ):
                dims = framing_decision.protection_dimensions
            else:
                dims = framing_decision.dimensions

            return dims

        # FitSource: canvas.effective_dimensions
        if source_canvas.effective_dimensions is not None and source in (
            FitSource.canvas_effective_dimensions,
            PreserveFromSourceCanvas.canvas_effective_dimensions,
        ):
            return DimensionsFloat(
                width=float(source_canvas.effective_dimensions.width),
                height=float(source_canvas.effective_dimensions.height),
            )

        # Default: use canvas.dimensions as is (no-op)
        return DimensionsFloat(
            width=float(source_canvas.dimensions.width),
            height=float(source_canvas.dimensions.height),
        )

    def _get_anamorphic_desqueezed_dimensions(
        self, source_canvas: Canvas, source_dimensions: DimensionsFloat
    ) -> DimensionsFloat:
        """Apply anamorphic desqueeze to `source_dimensions` using the template's
        target_anamorphic_squeeze. If the template's target_anamorphic_squeeze is zero, the input
        dimensions are returned unchanged.
        """
        if self.template.target_anamorphic_squeeze == 0 or not source_canvas.anamorphic_squeeze:
            return source_dimensions

        desqueeze_factor = (
            source_canvas.anamorphic_squeeze / self.template.target_anamorphic_squeeze
        )
        return DimensionsFloat(
            width=source_dimensions.width * desqueeze_factor,
            height=source_dimensions.height,
        )

    def _get_target_dimensions_and_scale(
        self,
        source_canvas: Canvas,
        framing_decision_id: Optional[FdlIdFramingDecision] = None,
    ) -> tuple[DimensionsFloat, float]:
        """Compute the output target dimensions and a scale factor mapping the desqueezed source
        into the template's `target_dimensions`, respecting the template's `fit_method`.
        """
        # Get target dimensions
        source_dims = self._get_source_dims(
            self.template.fit_source,
            source_canvas,
            framing_decision_id=framing_decision_id,
        )

        desqueezed_dimensions = self._get_anamorphic_desqueezed_dimensions(
            source_canvas, source_dims
        )

        # Calculate target aspect ratio
        scale_x = self.template.target_dimensions.width / desqueezed_dimensions.width
        scale_y = self.template.target_dimensions.height / desqueezed_dimensions.height

        # Apply fit method
        if self.template.fit_method == FitMethod.width:
            scale = scale_x
            return DimensionsFloat(
                width=self.template.target_dimensions.width,
                height=desqueezed_dimensions.height * scale,
            ), scale

        elif self.template.fit_method == FitMethod.height:
            scale = scale_y
            return DimensionsFloat(
                width=desqueezed_dimensions.width * scale,
                height=self.template.target_dimensions.height,
            ), scale

        elif self.template.fit_method == FitMethod.fit_all:
            scale = min(scale_x, scale_y)
            return DimensionsFloat(
                width=self.template.target_dimensions.width,
                height=self.template.target_dimensions.height,
            ), scale

        elif self.template.fit_method == FitMethod.fill:
            scale = max(scale_x, scale_y)
            return DimensionsFloat(
                width=self.template.target_dimensions.width,
                height=self.template.target_dimensions.height,
            ), scale

        raise ValueError(f"Invalid fit_method: {self.template.fit_method}")
