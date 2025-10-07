# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["DocumentUnzipAsyncResponse"]


class DocumentUnzipAsyncResponse(BaseModel):
    async_result_id: str = FieldInfo(alias="asyncResultId")
    """The ID of the async result for this job."""
