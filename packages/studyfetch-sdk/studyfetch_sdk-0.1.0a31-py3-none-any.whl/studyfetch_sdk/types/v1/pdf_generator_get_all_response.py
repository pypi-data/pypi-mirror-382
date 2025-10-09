# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from .pdf_generator.pdf_response import PdfResponse

__all__ = ["PdfGeneratorGetAllResponse"]

PdfGeneratorGetAllResponse: TypeAlias = List[PdfResponse]
