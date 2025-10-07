# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ....._utils import PropertyInfo

__all__ = ["HelpRequestResolveParams"]


class HelpRequestResolveParams(TypedDict, total=False):
    slug: Required[str]

    browser_agent_run_id: Required[Annotated[str, PropertyInfo(alias="browserAgentRunId")]]

    resolution: Required[str]
    """Resolution details for the help request"""
