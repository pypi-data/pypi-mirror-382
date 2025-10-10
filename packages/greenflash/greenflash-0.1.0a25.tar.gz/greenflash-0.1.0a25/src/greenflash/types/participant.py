# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["Participant"]


class Participant(BaseModel):
    id: str
    """The Greenflash participant ID."""

    anonymized: bool
    """Whether the participant's personal information is anonymized."""

    external_id: str = FieldInfo(alias="externalId")
    """Your external user ID (matches the externalUserId from the request)."""

    metadata: Dict[str, object]
    """Additional data about the participant."""

    tenant_id: str = FieldInfo(alias="tenantId")
    """The tenant this participant belongs to."""

    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)
    """When the participant was first created."""

    email: Optional[str] = None
    """The participant's email address."""

    name: Optional[str] = None
    """The participant's full name."""

    phone: Optional[str] = None
    """The participant's phone number."""

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)
    """When the participant was last updated."""
