"""CanavasTemplate model extension for the ASC Framing Decision List (FDL).

This module provides the `CanavasTemplate` model extension used by the FDL. It supplies a
post-initialisation hook that serves validators and convenience methods.
"""

from typing import Any, Optional

from .schema import _CanvasTemplate


class CanvasTemplate(_CanvasTemplate):
    """Template"""

    def model_post_init(self, __context: Optional[Any]) -> None:
        """
        This method is called after the model is initialized to calculate any necessary values or
        perform additional setup.
        """
        if self.maximum_dimensions and (
            self.maximum_dimensions.width < self.target_dimensions.width
            or self.maximum_dimensions.height < self.target_dimensions.height
        ):
            raise ValueError(
                "maximum_dimensions must be greater than or equal to target_dimensions"
            )
