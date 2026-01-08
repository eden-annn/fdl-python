import pytest
import fdl


@pytest.fixture
def test_framing_intent() -> fdl.FramingIntent:
    return fdl.FramingIntent(
        label="Test Framing",
        id=fdl.FdlId("TEST01"),
        aspect_ratio=fdl.DimensionsInt(width=16, height=9),
        protection=0.1,
    )


@pytest.fixture
def test_framing_intent2() -> fdl.FramingIntent:
    return fdl.FramingIntent(
        label="Test Framing 2 ",
        id=fdl.FdlId("TEST02"),
        aspect_ratio=fdl.DimensionsInt(width=16, height=9),
        protection=0.1,
    )


@pytest.fixture
def test_canvas() -> fdl.Canvas:
    return fdl.Canvas(
        label="Test Canvas",
        id=fdl.FdlId("CANVAS01"),
        source_canvas_id=fdl.FdlId("CANVAS01"),
        dimensions=fdl.DimensionsInt(width=1920, height=1080),
        effective_dimensions=fdl.DimensionsInt(width=1920, height=1080),
        photosite_dimensions=fdl.DimensionsInt(width=1920, height=1080),
        physical_dimensions=fdl.DimensionsFloat(width=36.0, height=24.0),
        anamorphic_squeeze=1.0,
    )


@pytest.fixture
def test_canvas_ana() -> fdl.Canvas:
    return fdl.Canvas(
        label="Test Canvas Ana",
        id=fdl.FdlId("CANVAS02"),
        source_canvas_id=fdl.FdlId("CANVAS02"),
        dimensions=fdl.DimensionsInt(width=4448, height=3096),
        anamorphic_squeeze=2.0,
    )


@pytest.fixture
def test_canvas_template() -> fdl.CanvasTemplate:
    return fdl.CanvasTemplate(
        label="Test Template",
        id=fdl.FdlId("TEMPLATE01"),
        target_dimensions=fdl.DimensionsInt(width=1920, height=1080),
        target_anamorphic_squeeze=1.0,
        fit_source=fdl.FitSource.framing_decision_dimensions,
        fit_method=fdl.FitMethod.width,
    )
