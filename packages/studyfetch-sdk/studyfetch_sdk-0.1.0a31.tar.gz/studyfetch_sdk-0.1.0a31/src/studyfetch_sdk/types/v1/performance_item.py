# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["PerformanceItem"]


class PerformanceItem(BaseModel):
    avg_score: str = FieldInfo(alias="avgScore")
    """Average score"""

    max_possible: float = FieldInfo(alias="maxPossible")
    """Maximum possible points"""

    performance_ratio: str = FieldInfo(alias="performanceRatio")
    """Performance ratio as percentage"""

    title: str
    """Criterion title"""
