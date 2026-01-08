import fdl


def test_canvas_template_processor_applies_squeeze_first(test_canvas_ana: fdl.Canvas) -> None:
    """Test that CanvasTemplateProcessor applies the squeeze factor before any scaling."""
    height = 500
    sph = 1.0

    template = fdl.CanvasTemplate(
        label="Test Template",
        id=fdl.FdlId("TEMPLATE01"),
        target_dimensions=fdl.DimensionsInt(width=0, height=height),
        target_anamorphic_squeeze=sph,
        fit_source=fdl.FitSource.canvas_dimensions,
        fit_method=fdl.FitMethod.height,
    )

    processor = fdl.CanvasTemplateProcessor(template)
    new_canvas = processor.create_canvas(test_canvas_ana)

    scale_factor = height / test_canvas_ana.dimensions.height
    desqueezed_width = test_canvas_ana.dimensions.width * (
        test_canvas_ana.anamorphic_squeeze or sph
    )
    scaled_desqueezed_width = fdl.calc.rounding(
        desqueezed_width * scale_factor, fdl.Round(even=fdl.Even.whole, mode=fdl.Mode.round)
    )

    assert new_canvas.dimensions.width == scaled_desqueezed_width


def test_canvas_template_preserves_anamorphic_squeeze_when_target_is_zero(
    test_canvas_ana: fdl.Canvas,
) -> None:
    """
    Test that if target_anamorphic_squeeze is 0, the source anamorphic_squeeze value is retained.
    """
    # Setup template with target_anamorphic_squeeze = 0
    template = fdl.CanvasTemplate(
        label="Test Template",
        id=fdl.FdlId("TEMPLATE01"),
        target_dimensions=fdl.DimensionsInt(width=1000, height=500),
        target_anamorphic_squeeze=0.0,
        fit_source=fdl.FitSource.canvas_dimensions,
        fit_method=fdl.FitMethod.width,
    )
    processor = fdl.CanvasTemplateProcessor(template)
    new_canvas = processor.create_canvas(test_canvas_ana)

    assert new_canvas.anamorphic_squeeze == test_canvas_ana.anamorphic_squeeze


def test_canvas_template_include_effective_dimensions_when_fit_source_does_not_fill_target_dimensions(
    test_canvas_ana: fdl.Canvas,
) -> None:
    """
    Test to ensure that canvas.effective_dimensions and canvas.effective_anchor_point values are
    newly created when fit_source does not fill the target_dimensions and the source Canvas did not
    include defined canvas.effective_dimensions.
    """
    # Setup template that creates pillar boxes
    template = fdl.CanvasTemplate(
        label="Test Template",
        id=fdl.FdlId("TEMPLATE01"),
        target_dimensions=fdl.DimensionsInt(width=2224, height=500),
        target_anamorphic_squeeze=1.0,
        fit_source=fdl.FitSource.canvas_dimensions,
        fit_method=fdl.FitMethod.height,
        maximum_dimensions=fdl.DimensionsInt(width=2224, height=500),
        pad_to_maximum=True,
    )
    processor = fdl.CanvasTemplateProcessor(template)
    new_canvas = processor.create_canvas(test_canvas_ana)

    scale_factor = 500 / test_canvas_ana.dimensions.height
    desqueezed_width = test_canvas_ana.dimensions.width * (
        test_canvas_ana.anamorphic_squeeze or 1.0
    )
    scaled_desqueezed_width = fdl.calc.rounding(
        desqueezed_width * scale_factor, fdl.Round(even=fdl.Even.whole, mode=fdl.Mode.round)
    )
    x = float((2224 - scaled_desqueezed_width) / 2)

    assert new_canvas.effective_dimensions
    assert new_canvas.effective_dimensions.width == scaled_desqueezed_width
    assert new_canvas.effective_dimensions.height == 500
    assert new_canvas.effective_anchor_point == fdl.PointFloat(x=x, y=0.0)
