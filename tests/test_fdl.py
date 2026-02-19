import pytest

import fdl


class TestFramingDecisionList:
    def test_add_framing_intent_duplicate_id(self, test_framing_intent: fdl.FramingIntent) -> None:
        """Test that add_framing_intent raises an error when adding duplicate intent IDs."""
        fdl_list = fdl.AscFramingDecisionList()
        fdl_list.add_framing_intent(test_framing_intent)
        with pytest.raises(Exception):
            fdl_list.add_framing_intent(test_framing_intent)

    def test_add_and_get_framing_intent(self, test_framing_intent: fdl.FramingIntent) -> None:
        """Test that a framing intent can be added and retrieved by its ID."""
        fdl_list = fdl.AscFramingDecisionList()
        fdl_list.add_framing_intent(test_framing_intent)
        result = fdl_list.get_framing_intent_by_id("TEST01")
        assert result is not None
        assert result.id == fdl.FdlId("TEST01")

    def test_set_default_framing_intent(
        self, test_framing_intent: fdl.FramingIntent, test_framing_intent2: fdl.FramingIntent
    ) -> None:
        """Test that set_default_framing_intent sets and updates the default intent correctly."""
        fdl_list = fdl.AscFramingDecisionList()
        fdl_list.add_framing_intent(test_framing_intent)

        assert fdl_list.default_framing_intent is None, (
            "The default framing intent should be None until explicitly set"
        )

        fdl_list.add_framing_intent(test_framing_intent2)
        assert fdl_list.default_framing_intent == None, (
            "Default framing intent should remain when adding a new framing intent"
        )

        fdl_list.set_default_framing_intent(test_framing_intent2.id)
        assert fdl_list.default_framing_intent == test_framing_intent2.id, (
            "Default framing intent should be updated to the new intent"
        )

    def test_add_canvas_duplicate_id(self, test_canvas: fdl.Canvas) -> None:
        """Test that add_canvas raises an error when adding duplicate canvas IDs."""
        fdl_list = fdl.AscFramingDecisionList()
        context = fdl.Context()
        fdl_list.add_context(context)
        context.add_canvas(test_canvas)
        with pytest.raises(Exception):
            context.add_canvas(test_canvas)

    def test_add_canvas_template_duplicate_id(
        self, test_canvas_template: fdl.CanvasTemplate
    ) -> None:
        """Test that add_canvas_template raises an error when adding duplicate template IDs."""
        fdl_list = fdl.AscFramingDecisionList()
        fdl_list.add_canvas_template(test_canvas_template)
        with pytest.raises(Exception):
            fdl_list.add_canvas_template(test_canvas_template)
