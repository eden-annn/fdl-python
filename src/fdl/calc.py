"""Helper module for the ASC Framing Decision List (FDL).

A collection of stand-alone functions used by the FDL package such as rounding helpers, framing
decision geometry, or anchor-point calculations.
"""

import math
from typing import Tuple, Optional, Union

from .schema import (
    DimensionsInt,
    DimensionsFloat,
    FramingIntent,
    PointFloat,
    Even,
    Mode,
    Round,
    AlignmentMethodVertical,
    AlignmentMethodHorizontal,
)
from .canvas import Canvas


def to_int_dimensions(dimensions: DimensionsFloat) -> DimensionsInt:
    """
    Convert floating dimensions to integer dimensions using the FDL-suggested default rounding.
    """
    return DimensionsInt(
        width=int(rounding(dimensions.width, Round(even=Even.whole, mode=Mode.round))),
        height=int(rounding(dimensions.height, Round(even=Even.whole, mode=Mode.round))),
    )


def rounding(value: float, round_config: Round) -> int:
    """Round floating values by the given FDL `Round` configuration."""
    if round_config.even == Even.whole:
        # Round to whole numbers
        if round_config.mode == Mode.up:
            return math.ceil(value)
        elif round_config.mode == Mode.down:
            return math.floor(value)
        else:
            return round(value)
    else:
        if round_config.mode == Mode.up:
            return int((value + 1) // 2 * 2)
        elif round_config.mode == Mode.down:
            return int(value // 2 * 2)
        else:
            return 2 * round(value / 2)


def calculate_framing_decision(
    canvas: Canvas, framing_intent: FramingIntent
) -> Tuple[DimensionsFloat, PointFloat, Optional[DimensionsFloat], Optional[PointFloat]]:
    """Compute FramingDecision geometry for `framing_intent` on `canvas`.

    Args:
        canvas: Canvas to create the framing decision for
        framing_intent: FramingIntent to create the framing decision from

    Returns:
        Tuple of (dimensions, anchor_point, protection_dimensions, protection_anchor_point)
    """
    # Get canvas dimensions
    if canvas.effective_dimensions:
        canvas_width = canvas.effective_dimensions.width
        canvas_height = canvas.effective_dimensions.height
    else:
        canvas_width = canvas.dimensions.width
        canvas_height = canvas.dimensions.height

    # Calculate aspect ratios
    intent_ar = framing_intent.aspect_ratio.width / framing_intent.aspect_ratio.height
    canvas_ar = canvas_width / canvas_height

    # Calculate decision dimensions
    if intent_ar > canvas_ar:
        decision_width = float(canvas_width)
        decision_height = decision_width / intent_ar
    else:
        decision_height = float(canvas_height)
        decision_width = decision_height * intent_ar

    dimensions = DimensionsFloat(width=decision_width, height=decision_height)
    protection_dimensions = None
    protection_anchor_point = None

    # Handle protection if specified
    if framing_intent.protection and framing_intent.protection > 0:
        protection_dimensions = dimensions
        protection_factor = 1.0 - framing_intent.protection
        dimensions = DimensionsFloat(
            width=dimensions.width * protection_factor,
            height=dimensions.height * protection_factor,
        )
        protection_anchor_point = get_anchor_point(
            canvas_width,
            canvas_height,
            protection_dimensions.width,
            protection_dimensions.height,
        )

    # Calculate anchor points
    anchor_point = get_anchor_point(
        canvas_width, canvas_height, dimensions.width, dimensions.height
    )

    return dimensions, anchor_point, protection_dimensions, protection_anchor_point


def get_anchor_point(
    canvas_width: Union[int, float],
    canvas_height: Union[int, float],
    target_width: Union[int, float],
    target_height: Union[int, float],
    alignment_vertical: AlignmentMethodVertical = AlignmentMethodVertical.center,
    alignment_horizontal: AlignmentMethodHorizontal = AlignmentMethodHorizontal.center,
) -> PointFloat:
    """Calculate anchor point based on alignment methods.

    Args:
        canvas_width: Width of the canvas
        canvas_height: Height of the canvas
        target_width: Width of the target area
        target_height: Height of the target area
        alignment_vertical: Vertical alignment method
        alignment_horizontal: Horizontal alignment method
    """
    # Calculate horizontal anchor point
    if alignment_horizontal == AlignmentMethodHorizontal.left:
        anchor_x = 0.0
    elif alignment_horizontal == AlignmentMethodHorizontal.center:
        anchor_x = (canvas_width - target_width) / 2
    else:  # right
        anchor_x = canvas_width - target_width

    # Calculate vertical anchor point
    if alignment_vertical == AlignmentMethodVertical.top:
        anchor_y = 0.0
    elif alignment_vertical == AlignmentMethodVertical.center:
        anchor_y = (canvas_height - target_height) / 2
    else:  # bottom
        anchor_y = canvas_height - target_height

    return PointFloat(x=float(anchor_x), y=float(anchor_y))
