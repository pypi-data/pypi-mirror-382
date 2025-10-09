# highlvlvpc_delete_image_response.py
from __future__ import annotations
from ..._models import BaseModel

__all__ = ["HighlvlvpcDeleteImageResponse"]

class HighlvlvpcDeleteImageResponse(BaseModel):
    success: bool
    """Whether the image deletion was successful."""

    message: str
    """A descriptive message about the deletion result."""
