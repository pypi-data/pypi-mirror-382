# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .performance_item import PerformanceItem

__all__ = [
    "AssignmentGraderGenerateReportResponse",
    "CriteriaAnalysis",
    "GradeDistribution",
    "Statistics",
    "Submission",
]


class CriteriaAnalysis(BaseModel):
    avg_score: float = FieldInfo(alias="avgScore")
    """Average score for this criterion"""

    max_possible: float = FieldInfo(alias="maxPossible")
    """Maximum possible points"""

    submission_count: float = FieldInfo(alias="submissionCount")
    """Number of submissions graded"""

    title: str
    """Criterion title"""


class GradeDistribution(BaseModel):
    a: float = FieldInfo(alias="A")
    """Number of A grades (90-100)"""

    b: float = FieldInfo(alias="B")
    """Number of B grades (80-89)"""

    c: float = FieldInfo(alias="C")
    """Number of C grades (70-79)"""

    d: float = FieldInfo(alias="D")
    """Number of D grades (60-69)"""

    f: float = FieldInfo(alias="F")
    """Number of F grades (0-59)"""


class Statistics(BaseModel):
    average_grade: str = FieldInfo(alias="averageGrade")
    """Average grade"""

    max_grade: str = FieldInfo(alias="maxGrade")
    """Maximum grade"""

    min_grade: str = FieldInfo(alias="minGrade")
    """Minimum grade"""

    standard_deviation: str = FieldInfo(alias="standardDeviation")
    """Standard deviation"""


class Submission(BaseModel):
    id: str
    """Submission ID"""

    created_at: datetime = FieldInfo(alias="createdAt")
    """Submission date"""

    grade: float
    """Grade percentage"""

    student_identifier: str = FieldInfo(alias="studentIdentifier")
    """Student identifier"""


class AssignmentGraderGenerateReportResponse(BaseModel):
    assignment_id: str = FieldInfo(alias="assignmentId")
    """Assignment ID"""

    criteria_analysis: List[CriteriaAnalysis] = FieldInfo(alias="criteriaAnalysis")
    """Analysis per criterion"""

    grade_distribution: GradeDistribution = FieldInfo(alias="gradeDistribution")
    """Grade distribution"""

    statistics: Statistics
    """Grade statistics"""

    strengths: List[PerformanceItem]
    """Top performing criteria"""

    submissions: List[Submission]
    """List of all submissions"""

    title: str
    """Assignment title"""

    total_submissions: float = FieldInfo(alias="totalSubmissions")
    """Total number of submissions"""

    weaknesses: List[PerformanceItem]
    """Criteria needing improvement"""
