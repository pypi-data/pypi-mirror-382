# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Annotated, TypeAlias, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo
from .shared_params.or_ import Or
from .shared_params.and_ import And

__all__ = ["MemoryListParams", "Filters"]


class MemoryListParams(TypedDict, total=False):
    container_tags: Annotated[SequenceNotStr[str], PropertyInfo(alias="containerTags")]
    """Optional tags this document should be containerized by.

    This can be an ID for your user, a project ID, or any other identifier you wish
    to use to group documents.
    """

    filters: Filters
    """Optional filters to apply to the search. Can be a JSON string or Query object."""

    include_content: Annotated[bool, PropertyInfo(alias="includeContent")]
    """Whether to include the content field in the response.

    Warning: This can make responses significantly larger.
    """

    limit: Union[str, float]
    """Number of items per page"""

    order: Literal["asc", "desc"]
    """Sort order"""

    page: Union[str, float]
    """Page number to fetch"""

    sort: Literal["createdAt", "updatedAt"]
    """Field to sort by"""


Filters: TypeAlias = Union[Or, And]
