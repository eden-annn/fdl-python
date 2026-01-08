import pytest
import fdl


def test_framing_decision_id_format(
    test_framing_intent: fdl.FramingIntent, test_canvas: fdl.Canvas
) -> None:
    """
    Test that FramingDecision.create_for_canvas returns a FramingDecision with an id formatted as
    `[canvas>id] [-] [framing_intent>id]`.
    """
    decision = test_canvas.add_framing_decision(test_framing_intent)
    expected_id = f"{test_canvas.id}-{test_framing_intent.id}"
    assert str(decision.id) == expected_id


@pytest.mark.parametrize(
    "canvas_width,canvas_height,aspect_width,aspect_height,expected_width,expected_height",
    [
        # Canvas 1.43:1 (4096x2866), intent 2:1 -> 4096x2048
        (4096, 2866, 2, 1, 4096, 2048),
        # Canvas 2.39:1 (4096x1716), intent 2:1 -> 3432x1716
        (4096, 1716, 2, 1, 3432, 1716),
        # Canvas 2:1 (4096x2048), intent 2:1 -> 4096x2048
        (4096, 2048, 2, 1, 4096, 2048),
        # Canvas 2:1 (4096x2048), intent 1.43:1 -> 2929x2048
        (4096, 2048, 143, 100, 2929, 2048),
    ],
)
def test_framing_decision_fits_within_canvas(
    canvas_width: int,
    canvas_height: int,
    aspect_width: int,
    aspect_height: int,
    expected_width: int,
    expected_height: int,
):
    """
    Test that FramingDecision fits in the Canvas without cropping, for various aspect ratios.
    """
    canvas = fdl.Canvas(
        label="Test Canvas",
        id=fdl.FdlId("CANVAS01"),
        source_canvas_id=fdl.FdlId("CANVAS01"),
        dimensions=fdl.DimensionsInt(width=canvas_width, height=canvas_height),
    )
    intent = fdl.FramingIntent(
        label="Test Intent",
        id=fdl.FdlId("INTENT01"),
        aspect_ratio=fdl.DimensionsInt(width=aspect_width, height=aspect_height),
        protection=0.0,
    )

    decision = canvas.add_framing_decision(intent)

    assert round(decision.dimensions.width) == expected_width
    assert round(decision.dimensions.height) == expected_height
