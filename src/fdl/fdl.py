"""The main ASC Framing Decision List (FDL) client module.

Provides an in-memory API for creating and manipulating ASC Framing Decision Lists (FDLs). Exposes
convenience helpers to add FDL models such as contexts, canvases, framing intents, framing decisions
and canvas templates, and to serialize/parse FDL documents.
"""

from typing import Any, Iterator, Optional, Union
from typing_extensions import Self

from pydantic import field_validator

from .context import Context
from .canvas import Canvas
from .template import CanvasTemplate
from .schema import FdlId, FramingIntent, FramingDecision, _AscFramingDecisionList


class AscFramingDecisionList(_AscFramingDecisionList):
    """FDL Client Class for providing helper methods to work with ASC Framing Decision Lists.

    This class provides convenience methods to manage FDL components, with their required
    validations, such as ensuring unique FDL IDs, and methods for serialization and deserialization.
    """

    @field_validator("framing_intents")
    @classmethod
    def validate_uniqueness_framing_intents(
        cls,
        framing_intents: Optional[list[FramingIntent]],
    ) -> Optional[list[FramingIntent]]:
        """Validate that all framing intent IDs are unique."""
        if framing_intents is None:
            return None

        seen = set()
        for framing_intent in framing_intents:
            framing_intent_id = framing_intent.id
            if str(framing_intent_id) in seen:
                raise ValueError(f"Framing intent ID {framing_intent_id!r} already exists")

            seen.add(str(framing_intent_id))

        return framing_intents

    @field_validator("canvas_templates")
    @classmethod
    def validate_uniqueness_canvas_templates(
        cls,
        canvas_templates: Optional[list[CanvasTemplate]],
    ) -> Optional[list[CanvasTemplate]]:
        """Validate that all CanvasTemplate IDs are unique."""
        if canvas_templates is None:
            return None

        seen = set()
        for canvas_template in canvas_templates:
            canvas_template_id = canvas_template.id
            if str(canvas_template_id) in seen:
                raise ValueError(f"CanvasTemplate ID {canvas_template_id!r} already exists")

            seen.add(str(canvas_template_id))

        return canvas_templates

    def add_context(self, context: Context) -> None:
        """Add a new context in the FDL."""
        if not self.contexts:
            self.contexts = []

        self.contexts.append(context)

    def add_framing_intent(self, framing_intent: FramingIntent) -> FramingIntent:
        """Add a new framing intent to the FDL.

        Raises:
            ValueError: If the framing intent ID already exists
        """
        if not self.framing_intents:
            self.framing_intents = []

        # Use variable assignment to trigger the pydantic validator
        self.framing_intents = self.framing_intents + [framing_intent]

        return framing_intent

    def add_framing_decision_to_canvas(
        self,
        framing_intent: Union[FramingIntent, FdlId],
        canvas: Union[Canvas, FdlId],
        label: Optional[str] = None,
    ) -> FramingDecision:
        """Add a new framing decision to a canvas based on a framing intent.

        Both the framing intent and canvas must exist in the current FDL instance of this class.
        """
        if isinstance(framing_intent, FdlId):
            framing_intent = self.get_framing_intent_by_id(framing_intent)

        if isinstance(canvas, FdlId):
            canvas = self.get_canvas_by_id(canvas)

        framing_decision = canvas.add_framing_decision(framing_intent, label=label)

        return framing_decision

    def add_canvas_template(self, canvas_template: CanvasTemplate) -> CanvasTemplate:
        """Add a `CanvasTemplate`.

        Raises:
            ValueError: if a template with the same `id` already exists.
        """
        if not self.canvas_templates:
            self.canvas_templates = []

        # Use variable assignment to trigger the pydantic validator
        self.canvas_templates = self.canvas_templates + [canvas_template]

        return canvas_template

    def get_canvas_by_id(
        self, canvas_id: Union[str, FdlId], from_context: Optional[Context] = None
    ) -> Canvas:
        """Get a canvas by its ID. Searches within the specified context if provided"""
        canvas_id = FdlId.model_validate(str(canvas_id))

        for context in (from_context,) if from_context else self.iter_contexts():
            if not context.canvases:
                continue

            try:
                return context.get_canvas_by_id(canvas_id)
            except ValueError:
                pass

        raise ValueError(f"Canvas ID '{canvas_id}' not found in any context")

    def get_framing_intent_by_id(self, framing_intent_id: Union[str, FdlId]) -> FramingIntent:
        """Get a framing intent by its ID."""
        fdl_id = FdlId.model_validate(str(framing_intent_id))
        for framing_intent in self.framing_intents or []:
            if framing_intent.id == fdl_id:
                return framing_intent

        raise ValueError(f"Framing intent ID '{framing_intent_id}' not found")

    def iter_framing_intents(self) -> Iterator[FramingIntent]:
        """Yield each `FramingIntent` present in the FDL."""
        if not self.framing_intents:
            return

        for framing_intent in self.framing_intents:
            yield framing_intent

    def iter_canvas_templates(self) -> Iterator[CanvasTemplate]:
        """Yield each `CanvasTemplate` present in the FDL."""
        if not self.canvas_templates:
            return

        for canvas_template in self.canvas_templates:
            yield canvas_template

    def iter_contexts(self) -> Iterator[Context]:
        """Yield each `Context` present in the FDL."""
        if not self.contexts:
            return

        for context in self.contexts:
            yield context

    def set_default_framing_intent(self, framing_intent_id: Union[str, FdlId]) -> None:
        """Set the default framing intent for the FDL.

        Raises:
            ValueError: If the framing intent ID doesn't exist
        """
        self.default_framing_intent = FdlId.model_validate(str(framing_intent_id))

    def to_dict(self) -> dict[str, Any]:
        """Convert the FDL to a dictionary."""
        return self.model_dump()

    def to_file(self, file_path: str, indent: int = 2) -> None:
        """Write the current FDL contents into a FDL file.

        Args:
            file_path: Path to the output FDL file
            indent: Number of spaces for indentation
        """
        with open(file_path, "w", encoding="utf-8") as _f:
            _f.write(self.to_json(indent=indent))

    def to_json(self, indent: int = 2) -> str:
        """Convert the FDL to a JSON string.

        Args:
            indent: Number of spaces for indentation

        Returns:
            JSON string representation of the FDL
        """
        return self.model_dump_json(indent=indent)

    @classmethod
    def from_dict(cls, dict_data: dict[str, Any]) -> Self:
        """Create a FramingDecisionList from a dictionary.

        Args:
            dict_data: Dictionary representation of an FDL
        """
        return cls.model_validate(dict_data)

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create a FramingDecisionList from a JSON string.

        Args:
            json_str: JSON string representation of an FDL
        """
        return cls.from_dict(cls.model_validate_json(json_str).model_dump())

    @classmethod
    def from_file(cls, file_path: str) -> Self:
        """Create a FramingDecisionList from a FDL file."""
        with open(file_path, "r", encoding="utf-8") as _f:
            instance = cls.from_json(_f.read())

        return instance
