# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ....._models import BaseModel

__all__ = ["HelpRequestResolveResponse"]


class HelpRequestResolveResponse(BaseModel):
    id: str

    browser_agent_run_id: str = FieldInfo(alias="browserAgentRunId")

    created_at: datetime = FieldInfo(alias="createdAt")

    org_id: str = FieldInfo(alias="orgId")

    request: str

    resolution: Optional[str] = None

    resolved_at: Optional[datetime] = FieldInfo(alias="resolvedAt", default=None)

    status: str
