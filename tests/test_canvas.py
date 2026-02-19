import pytest
from typing import Optional

import fdl


@pytest.mark.parametrize(
    "dimensions,effective_dimensions,effective_anchor_point,expected_anchor_point",
    [
        (
            fdl.DimensionsInt(width=4448, height=3096),
            fdl.DimensionsInt(width=4006, height=2788),
            None,
            fdl.PointFloat(x=221, y=154),
        ),
        (
            fdl.DimensionsInt(width=4448, height=3096),
            fdl.DimensionsInt(width=4006, height=2788),
            fdl.PointFloat(x=10, y=10),
            fdl.PointFloat(x=10, y=10),
        ),
        (
            fdl.DimensionsInt(width=1920, height=1080),
            fdl.DimensionsInt(width=1920, height=720),
            None,
            fdl.PointFloat(x=0, y=180),
        ),
        (
            fdl.DimensionsInt(width=1920, height=1080),
            None,
            None,
            None,
        ),
    ],
)
def test_canvas_effective_anchor_point(
    dimensions: fdl.DimensionsInt,
    effective_dimensions: Optional[fdl.DimensionsInt],
    effective_anchor_point: Optional[fdl.PointFloat],
    expected_anchor_point: Optional[fdl.PointFloat],
) -> None:
    """
    Test that Canvas.effective_anchor_point is generated when effective_dimensions is specified.
    """
    canvas = fdl.Canvas(
        label="Test Canvas",
        id=fdl.FdlId("CANVAS01"),
        source_canvas_id=fdl.FdlId("CANVAS01"),
        dimensions=dimensions,
        effective_dimensions=effective_dimensions,
        effective_anchor_point=effective_anchor_point,
        photosite_dimensions=None,
        physical_dimensions=None,
        anamorphic_squeeze=1.0,
    )

    assert canvas.effective_anchor_point == expected_anchor_point
