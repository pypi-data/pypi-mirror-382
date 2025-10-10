# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo
from .shared_params.or_ import Or
from .shared_params.and_ import And

__all__ = ["SearchMemoriesParams", "Filters", "Include"]


class SearchMemoriesParams(TypedDict, total=False):
    q: Required[str]
    """Search query string"""

    container_tag: Annotated[str, PropertyInfo(alias="containerTag")]
    """Optional tag this search should be containerized by.

    This can be an ID for your user, a project ID, or any other identifier you wish
    to use to filter memories.
    """

    filters: Filters
    """Optional filters to apply to the search. Can be a JSON string or Query object."""

    include: Include

    limit: int
    """Maximum number of results to return"""

    rerank: bool
    """If true, rerank the results based on the query.

    This is helpful if you want to ensure the most relevant results are returned.
    """

    rewrite_query: Annotated[bool, PropertyInfo(alias="rewriteQuery")]
    """If true, rewrites the query to make it easier to find documents.

    This increases the latency by about 400ms
    """

    threshold: float
    """Threshold / sensitivity for memories selection.

    0 is least sensitive (returns most memories, more results), 1 is most sensitive
    (returns lesser memories, accurate results)
    """


Filters: TypeAlias = Union[Or, And]


class Include(TypedDict, total=False):
    documents: bool

    forgotten_memories: Annotated[bool, PropertyInfo(alias="forgottenMemories")]
    """If true, include forgotten memories in search results.

    Forgotten memories are memories that have been explicitly forgotten or have
    passed their expiration date.
    """

    related_memories: Annotated[bool, PropertyInfo(alias="relatedMemories")]

    summaries: bool
