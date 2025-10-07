# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ...._models import BaseModel

__all__ = ["EntryPostResponse"]


class EntryPostResponse(BaseModel):
    success: bool
    """Whether the event was emitted successfully."""
