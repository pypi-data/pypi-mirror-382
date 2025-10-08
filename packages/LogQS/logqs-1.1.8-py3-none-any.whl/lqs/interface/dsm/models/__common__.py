from enum import Enum

from lqs.interface.base.models.__common__ import (  # noqa: F401
    CommonModel,
    DataResponseModel,
    TimeSeriesModel,
    PaginationModel,
    PatchOperation,
    JSONFilter,
    optional_field,
    Int64,
)


class ProcessState(str, Enum):
    ready = "ready"
    queued = "queued"
    processing = "processing"
    finalizing = "finalizing"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"
    archived = "archived"


class ProcessType(str, Enum):
    ingestion = "ingestion"
    ingestion_part = "ingestion_part"
    digestion = "digestion"
    digestion_part = "digestion_part"


class JobType(str, Enum):
    ingestion = "ingestion"
    post_ingestion = "post_ingestion"
    failed_ingestion = "failed_ingestion"

    ingestion_part = "ingestion_part"
    post_ingestion_part = "post_ingestion_part"
    failed_ingestion_part = "failed_ingestion_part"

    digestion = "digestion"
    post_digestion = "post_digestion"
    failed_digestion = "failed_digestion"

    digestion_part = "digestion_part"
    post_digestion_part = "post_digestion_part"
    failed_digestion_part = "failed_digestion_part"

    extraction = "extraction"
    post_extraction = "post_extraction"
    failed_extraction = "failed_extraction"

    inference = "inference"
    post_inference = "post_inference"
    failed_inference = "failed_inference"

    copy = "copy"
    post_copy = "post_copy"
    failed_copy = "failed_copy"

    rectify = "rectify"
    post_rectify = "post_rectify"
    failed_rectify = "failed_rectify"
