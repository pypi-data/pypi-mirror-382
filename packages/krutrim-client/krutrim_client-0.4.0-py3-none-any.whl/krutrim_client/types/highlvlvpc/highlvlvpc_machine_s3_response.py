

from typing import Optional

from ..._models import BaseModel

__all__ = ["ImageMachineResponse"]


class ImageMachineResponse(BaseModel):
    message: Optional[str] = None