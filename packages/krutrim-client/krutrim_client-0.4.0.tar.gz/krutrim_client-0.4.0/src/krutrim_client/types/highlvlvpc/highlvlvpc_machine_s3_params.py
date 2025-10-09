

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ImageMachineParams"]


class ImageMachineParams(TypedDict, total=False):
    disk_format: Required[Annotated[str, PropertyInfo(alias="diskFormat")]]
    """The format of the disk image."""

    image: Required[str]
    """A URL to the image file."""