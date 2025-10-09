# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .document_status import DocumentStatus

__all__ = ["Document", "Version", "ScrapeJob"]


class Version(BaseModel):
    id: str
    """Unique identifier of the document version"""

    content: str
    """Content of the document version"""

    created_at: datetime = FieldInfo(alias="createdAt")
    """When the document version was created"""

    document_id: str = FieldInfo(alias="documentId")
    """ID of the document this version belongs to"""

    language: str
    """Language of the document version"""

    metadata: Dict[str, object]
    """Optional metadata associated with the document version"""

    modified_at: datetime = FieldInfo(alias="modifiedAt")
    """When the document version was last modified"""

    org_id: str = FieldInfo(alias="orgId")
    """Organization ID that owns this document version"""

    original_sentences: List[str] = FieldInfo(alias="originalSentences")
    """Array of original sentences from the source"""

    status: DocumentStatus
    """Status of the document. Valid options: DRAFT, REVIEW, APPROVED, ARCHIVED."""

    title: str
    """Title of the document version"""

    version_number: float = FieldInfo(alias="versionNumber")
    """Version number of this document version"""


class ScrapeJob(BaseModel):
    id: str
    """Unique identifier of the scrape job"""

    created_at: datetime = FieldInfo(alias="createdAt")
    """When the scrape job was created"""

    initiated_by: str = FieldInfo(alias="initiatedBy")
    """User ID who initiated the scrape job"""

    modified_at: datetime = FieldInfo(alias="modifiedAt")
    """When the scrape job was last modified"""

    name: str
    """Name of the scrape job"""

    org_id: str = FieldInfo(alias="orgId")
    """Organization ID that owns this scrape job"""

    status: Literal["PENDING", "IN_PROGRESS", "RUNNING", "COMPLETED", "FAILED"]
    """Status of the scrape job.

    Valid options: PENDING, IN_PROGRESS, RUNNING, COMPLETED, FAILED.
    """

    pages: Optional[List[str]] = None
    """Array of scraped pages"""

    url: Optional[str] = None
    """Optional URL that was scraped"""


class Document(BaseModel):
    id: str
    """Unique identifier of the document"""

    assignee: str
    """User ID of the person assigned to this document"""

    content: str
    """use versions.content"""

    created_at: datetime = FieldInfo(alias="createdAt")
    """When the document was created"""

    modified_at: datetime = FieldInfo(alias="modifiedAt")
    """When the document was last modified"""

    optimized: bool
    """Whether the document has been optimized"""

    org_id: str = FieldInfo(alias="orgId")
    """Organization ID that owns this document"""

    title: str
    """use versions.title instead"""

    versions: List[Version]
    """Array of document versions"""

    active_version_id: Optional[str] = FieldInfo(alias="activeVersionId", default=None)
    """ID of the currently active version of this document"""

    scrape_job: Optional[ScrapeJob] = FieldInfo(alias="scrapeJob", default=None)
    """Optional scrape job that generated this document"""

    scrape_job_id: Optional[str] = FieldInfo(alias="scrapeJobId", default=None)
    """Optional ID of the scrape job that generated this document"""
