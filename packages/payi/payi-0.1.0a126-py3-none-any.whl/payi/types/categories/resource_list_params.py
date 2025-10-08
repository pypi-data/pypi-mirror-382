# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ResourceListParams"]


class ResourceListParams(TypedDict, total=False):
    category: Required[str]

    cursor: str

    limit: int

    sort_ascending: bool
