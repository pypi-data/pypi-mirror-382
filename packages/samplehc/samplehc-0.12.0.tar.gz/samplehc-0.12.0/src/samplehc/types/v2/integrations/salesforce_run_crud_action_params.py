# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Literal, Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["SalesforceRunCrudActionParams"]


class SalesforceRunCrudActionParams(TypedDict, total=False):
    crud_action_type: Required[
        Annotated[Literal["create", "update", "upsert", "delete", "retrieve"], PropertyInfo(alias="crudActionType")]
    ]

    resource_type: Required[Annotated[str, PropertyInfo(alias="resourceType")]]

    resource_body: Annotated[Dict[str, object], PropertyInfo(alias="resourceBody")]

    resource_id: Annotated[str, PropertyInfo(alias="resourceId")]
