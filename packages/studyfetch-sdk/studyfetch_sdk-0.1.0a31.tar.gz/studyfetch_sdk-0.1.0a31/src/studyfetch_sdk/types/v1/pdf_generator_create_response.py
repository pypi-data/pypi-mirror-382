# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .pdf_generator.pdf_response import PdfResponse

__all__ = ["PdfGeneratorCreateResponse"]


class PdfGeneratorCreateResponse(BaseModel):
    presentation: Optional[PdfResponse] = None

    success: Optional[bool] = None
