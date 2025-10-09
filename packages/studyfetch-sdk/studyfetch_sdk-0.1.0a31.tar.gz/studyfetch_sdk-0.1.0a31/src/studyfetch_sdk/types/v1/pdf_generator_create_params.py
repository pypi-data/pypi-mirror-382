# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["PdfGeneratorCreateParams"]


class PdfGeneratorCreateParams(TypedDict, total=False):
    locale: Required[str]
    """Locale/language for the presentation (e.g., en-US, es-ES, fr-FR)"""

    number_of_slides: Required[Annotated[float, PropertyInfo(alias="numberOfSlides")]]
    """Number of slides to generate"""

    topic: Required[str]
    """The topic for the PDF presentation"""
