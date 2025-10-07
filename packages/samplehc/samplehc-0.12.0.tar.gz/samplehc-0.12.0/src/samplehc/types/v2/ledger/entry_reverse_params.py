# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["EntryReverseParams"]


class EntryReverseParams(TypedDict, total=False):
    metadata: Dict[str, object]
    """Any optional metadata to associate with the reversal entry."""

    posted_at: Annotated[str, PropertyInfo(alias="postedAt")]
    """The date and time the reversal entry was posted."""
