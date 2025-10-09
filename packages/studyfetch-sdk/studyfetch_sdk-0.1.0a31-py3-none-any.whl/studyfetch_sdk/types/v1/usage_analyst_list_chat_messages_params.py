# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._types import SequenceNotStr
from ..._utils import PropertyInfo

__all__ = ["UsageAnalystListChatMessagesParams"]


class UsageAnalystListChatMessagesParams(TypedDict, total=False):
    group_ids: Annotated[SequenceNotStr[str], PropertyInfo(alias="groupIds")]
    """Array of group IDs to filter"""

    user_id: Annotated[str, PropertyInfo(alias="userId")]
    """User ID to get chat messages for"""
