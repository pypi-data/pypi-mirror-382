# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ChatAnalyticsResponse", "Summary", "UserStat"]


class Summary(BaseModel):
    average_messages_per_user: float = FieldInfo(alias="averageMessagesPerUser")
    """Average messages per user"""

    engagement: object
    """Engagement metrics"""

    summary: str
    """Natural language summary of chat usage"""

    top_topics: List[str] = FieldInfo(alias="topTopics")
    """Top topics discussed"""

    total_messages: float = FieldInfo(alias="totalMessages")
    """Total messages"""

    total_sessions: float = FieldInfo(alias="totalSessions")
    """Total chat sessions"""

    total_users: float = FieldInfo(alias="totalUsers")
    """Total unique users"""

    overall_average_prompting_score: Optional[float] = FieldInfo(alias="overallAveragePromptingScore", default=None)
    """Overall average prompting score (1-4 scale)"""

    overall_average_responsibility_score: Optional[float] = FieldInfo(
        alias="overallAverageResponsibilityScore", default=None
    )
    """Overall average responsibility score (1-4 scale)"""

    overall_prompting_distribution: Optional[object] = FieldInfo(alias="overallPromptingDistribution", default=None)
    """Overall prompting score distribution"""

    overall_responsibility_distribution: Optional[object] = FieldInfo(
        alias="overallResponsibilityDistribution", default=None
    )
    """Overall responsibility score distribution"""


class UserStat(BaseModel):
    average_messages_per_session: float = FieldInfo(alias="averageMessagesPerSession")
    """Average messages per session"""

    average_session_duration: float = FieldInfo(alias="averageSessionDuration")
    """Average session duration in minutes"""

    first_active: datetime = FieldInfo(alias="firstActive")
    """First active date"""

    last_active: datetime = FieldInfo(alias="lastActive")
    """Last active date"""

    top_topics: List[str] = FieldInfo(alias="topTopics")
    """Top topics discussed"""

    total_messages: float = FieldInfo(alias="totalMessages")
    """Total messages sent by user"""

    total_sessions: float = FieldInfo(alias="totalSessions")
    """Total chat sessions"""

    user_id: str = FieldInfo(alias="userId")
    """User ID"""

    average_prompting_score: Optional[float] = FieldInfo(alias="averagePromptingScore", default=None)
    """Average prompting score (1-4 scale)"""

    average_responsibility_score: Optional[float] = FieldInfo(alias="averageResponsibilityScore", default=None)
    """Average responsibility score (1-4 scale)"""

    email: Optional[str] = None
    """User email"""

    group_ids: Optional[List[str]] = FieldInfo(alias="groupIds", default=None)
    """Group IDs associated with the user"""

    name: Optional[str] = None
    """User name"""

    prompting_distribution: Optional[object] = FieldInfo(alias="promptingDistribution", default=None)
    """Prompting score distribution"""

    responsibility_distribution: Optional[object] = FieldInfo(alias="responsibilityDistribution", default=None)
    """Responsibility score distribution"""

    total_graded_messages: Optional[float] = FieldInfo(alias="totalGradedMessages", default=None)
    """Total messages graded"""


class ChatAnalyticsResponse(BaseModel):
    generated_at: datetime = FieldInfo(alias="generatedAt")
    """Date when analytics were generated"""

    summary: Summary
    """Analytics summary"""

    user_stats: List[UserStat] = FieldInfo(alias="userStats")
    """User statistics"""
