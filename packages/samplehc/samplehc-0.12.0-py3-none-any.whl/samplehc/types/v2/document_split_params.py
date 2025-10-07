# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["DocumentSplitParams", "Document", "SplitDescription"]


class DocumentSplitParams(TypedDict, total=False):
    document: Required[Document]
    """The document to be split."""

    split_description: Required[Annotated[Iterable[SplitDescription], PropertyInfo(alias="splitDescription")]]
    """Split description configuration."""

    split_rules: Annotated[str, PropertyInfo(alias="splitRules")]
    """Optional split rules prompt for the splitter."""


class Document(TypedDict, total=False):
    id: Required[str]

    file_name: Required[Annotated[str, PropertyInfo(alias="fileName")]]


class SplitDescription(TypedDict, total=False):
    description: Required[str]

    name: Required[str]

    partition_key: Annotated[str, PropertyInfo(alias="partitionKey")]
