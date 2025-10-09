# highlvlvpc_delete_image_params.py
from __future__ import annotations
from typing_extensions import Required, TypedDict

__all__ = ["HighlvlvpcDeleteImageParams"]

class HighlvlvpcImageParams(TypedDict, total=False):
    image_krn: Required[str]
    """The full URN of the image to delete."""


