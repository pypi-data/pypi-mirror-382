# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = ["TemplateRenderDocumentParams", "Variables", "VariablesUnionMember0"]


class TemplateRenderDocumentParams(TypedDict, total=False):
    slug: Required[str]
    """The slug of the template to use."""

    variables: Required[Dict[str, Variables]]
    """Variables for the template.

    Accepts strings, arrays of objects for tables, or nested templates via
    `{ type: 'template', slug, variables }`.
    """


class VariablesUnionMember0(TypedDict, total=False):
    slug: Required[str]

    type: Required[Literal["template"]]

    variables: Required[Dict[str, object]]


Variables: TypeAlias = Union[VariablesUnionMember0, Iterable[Dict[str, str]], str]
