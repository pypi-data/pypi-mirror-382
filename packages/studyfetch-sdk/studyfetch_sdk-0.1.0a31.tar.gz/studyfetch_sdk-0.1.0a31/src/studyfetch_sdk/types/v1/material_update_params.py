# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

__all__ = ["MaterialUpdateParams", "Reference"]


class MaterialUpdateParams(TypedDict, total=False):
    references: Iterable[Reference]
    """Array of references to update (optional)"""


class Reference(TypedDict, total=False):
    title: Required[str]
    """Reference title"""

    url: str
    """Reference URL (optional)"""
