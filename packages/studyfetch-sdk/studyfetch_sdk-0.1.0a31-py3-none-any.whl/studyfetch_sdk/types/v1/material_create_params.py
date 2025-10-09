# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .content_param import ContentParam
from .reference_param import ReferenceParam

__all__ = ["MaterialCreateParams"]


class MaterialCreateParams(TypedDict, total=False):
    content: Required[ContentParam]
    """Content details"""

    name: Required[str]
    """Name of the material"""

    folder_id: Annotated[str, PropertyInfo(alias="folderId")]
    """Folder ID to place the material in"""

    references: Iterable[ReferenceParam]
    """References that this material cites"""
