# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["PdfResponse", "Transcript"]


class Transcript(BaseModel):
    description_of_page: str = FieldInfo(alias="descriptionOfPage")
    """Description of the slide content and OCR text"""

    page_num: float = FieldInfo(alias="pageNum")
    """Page number of the slide"""


class PdfResponse(BaseModel):
    api_id: str = FieldInfo(alias="_id")
    """PDF presentation ID"""

    created_at: datetime = FieldInfo(alias="createdAt")
    """Creation timestamp"""

    locale: str
    """Locale of the presentation"""

    number_of_slides: float = FieldInfo(alias="numberOfSlides")
    """Number of slides"""

    organization_id: str = FieldInfo(alias="organizationId")
    """Organization ID"""

    topic: str
    """Topic of the presentation"""

    transcript: List[Transcript]
    """Transcript of each slide"""

    updated_at: datetime = FieldInfo(alias="updatedAt")
    """Update timestamp"""

    url: str
    """URL to the generated PDF on S3"""

    user_id: Optional[str] = FieldInfo(alias="userId", default=None)
    """User ID"""
