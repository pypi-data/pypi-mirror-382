# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ...._models import BaseModel

__all__ = ["EntryReverseResponse"]


class EntryReverseResponse(BaseModel):
    success: bool
    """Whether the reversal entry was created successfully."""
