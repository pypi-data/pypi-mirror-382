# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["AccountWriteoffParams"]


class AccountWriteoffParams(TypedDict, total=False):
    order_id: Required[Annotated[str, PropertyInfo(alias="orderId")]]

    description: Required[str]
    """The description of the write-off."""

    metadata: Dict[str, object]
    """Any optional metadata to associate with the write-off."""

    posted_at: Annotated[str, PropertyInfo(alias="postedAt")]
    """The date and time to post the write-off."""
