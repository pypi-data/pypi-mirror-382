# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["MaterialGetJobStatusResponse", "Progress", "ResultSummary"]


class Progress(BaseModel):
    current_batch: Optional[float] = FieldInfo(alias="currentBatch", default=None)
    """Current batch being processed"""

    percentage: Optional[float] = None
    """Completion percentage (0-100)"""

    processed_images: Optional[float] = FieldInfo(alias="processedImages", default=None)
    """Images processed so far"""

    total_batches: Optional[float] = FieldInfo(alias="totalBatches", default=None)
    """Total number of batches"""

    total_images: Optional[float] = FieldInfo(alias="totalImages", default=None)
    """Total images to process"""


class ResultSummary(BaseModel):
    images_processed: Optional[float] = FieldInfo(alias="imagesProcessed", default=None)
    """Number of images processed"""

    processing_time_ms: Optional[float] = FieldInfo(alias="processingTimeMs", default=None)
    """Total processing time in milliseconds"""

    text_extracted: Optional[bool] = FieldInfo(alias="textExtracted", default=None)
    """Whether text was extracted"""

    text_length: Optional[float] = FieldInfo(alias="textLength", default=None)
    """Length of extracted text"""


class MaterialGetJobStatusResponse(BaseModel):
    completed_at: Optional[datetime] = FieldInfo(alias="completedAt", default=None)
    """Job completion time"""

    error: Optional[str] = None
    """Error message if job failed"""

    job_id: Optional[str] = FieldInfo(alias="jobId", default=None)
    """Unique job identifier"""

    progress: Optional[Progress] = None

    result_summary: Optional[ResultSummary] = FieldInfo(alias="resultSummary", default=None)

    started_at: Optional[datetime] = FieldInfo(alias="startedAt", default=None)
    """Job start time"""

    status: Optional[Literal["pending", "running", "completed", "failed", "cancelled"]] = None
    """Current job status"""
