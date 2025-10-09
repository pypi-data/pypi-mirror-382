# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["Reference"]


class Reference(BaseModel):
    title: str
    """Reference title"""

    url: Optional[str] = None
    """Reference URL"""
