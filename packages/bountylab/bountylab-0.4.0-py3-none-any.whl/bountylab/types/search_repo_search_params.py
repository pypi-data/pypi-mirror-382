# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = [
    "SearchRepoSearchParams",
    "Filters",
    "FiltersUnionMember0",
    "FiltersUnionMember1",
    "FiltersUnionMember2",
    "FiltersUnionMember3",
    "FiltersUnionMember4",
    "FiltersUnionMember5",
    "FiltersUnionMember6",
    "FiltersUnionMember7",
    "FiltersUnionMember8",
    "FiltersUnionMember9",
    "FiltersUnionMember10",
    "FiltersUnionMember11",
    "FiltersUnionMember12",
    "FiltersUnionMember13",
    "FiltersUnionMember14",
    "FiltersUnionMember15",
    "FiltersUnionMember16",
    "FiltersUnionMember17",
    "FiltersUnionMember18",
    "FiltersUnionMember19",
    "FiltersUnionMember20",
    "FiltersUnionMember21",
    "FiltersUnionMember22",
    "FiltersUnionMember23",
    "FiltersUnionMember24",
    "FiltersUnionMember25",
    "FiltersRepoCompositeFilter",
    "FiltersRepoCompositeFilterFilter",
    "FiltersRepoCompositeFilterFilterUnionMember0",
    "FiltersRepoCompositeFilterFilterUnionMember1",
    "FiltersRepoCompositeFilterFilterUnionMember2",
    "FiltersRepoCompositeFilterFilterUnionMember3",
    "FiltersRepoCompositeFilterFilterUnionMember4",
    "FiltersRepoCompositeFilterFilterUnionMember5",
    "FiltersRepoCompositeFilterFilterUnionMember6",
    "FiltersRepoCompositeFilterFilterUnionMember7",
    "FiltersRepoCompositeFilterFilterUnionMember8",
    "FiltersRepoCompositeFilterFilterUnionMember9",
    "FiltersRepoCompositeFilterFilterUnionMember10",
    "FiltersRepoCompositeFilterFilterUnionMember11",
    "FiltersRepoCompositeFilterFilterUnionMember12",
    "FiltersRepoCompositeFilterFilterUnionMember13",
    "FiltersRepoCompositeFilterFilterUnionMember14",
    "FiltersRepoCompositeFilterFilterUnionMember15",
    "FiltersRepoCompositeFilterFilterUnionMember16",
    "FiltersRepoCompositeFilterFilterUnionMember17",
    "FiltersRepoCompositeFilterFilterUnionMember18",
    "FiltersRepoCompositeFilterFilterUnionMember19",
    "FiltersRepoCompositeFilterFilterUnionMember20",
    "FiltersRepoCompositeFilterFilterUnionMember21",
    "FiltersRepoCompositeFilterFilterUnionMember22",
    "FiltersRepoCompositeFilterFilterUnionMember23",
    "FiltersRepoCompositeFilterFilterUnionMember24",
    "FiltersRepoCompositeFilterFilterUnionMember25",
]


class SearchRepoSearchParams(TypedDict, total=False):
    query: Required[str]
    """
    Natural language search query for semantic search across repository README and
    description using vector embeddings
    """

    filters: Optional[Filters]
    """Optional filters for narrowing search results.

    Supports filtering on: githubId, ownerLogin, name, stargazerCount, language,
    totalIssuesCount, totalIssuesOpen, totalIssuesClosed, lastContributorLocations.

    Filter structure:

    - Field filters: { field: "fieldName", op: "Eq"|"In"|"Gte"|"Lte", value:
      string|number|array }
    - Composite filters: { op: "And"|"Or", filters: [...] }

    Supported operators:

    - String fields: Eq (exact match), In (one of array)
    - Number fields: Eq (exact), In (one of array), Gte (>=), Lte (<=)
    - Use And/Or to combine multiple filters
    """

    max_results: Annotated[int, PropertyInfo(alias="maxResults")]
    """Maximum number of results to return (default: 100, max: 1000)"""


class FiltersUnionMember0(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUnionMember1(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember2(TypedDict, total=False):
    field: Required[Literal["ownerLogin"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUnionMember3(TypedDict, total=False):
    field: Required[Literal["ownerLogin"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember4(TypedDict, total=False):
    field: Required[Literal["name"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUnionMember5(TypedDict, total=False):
    field: Required[Literal["name"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember6(TypedDict, total=False):
    field: Required[Literal["stargazerCount"]]

    op: Required[Literal["Eq"]]

    value: Required[float]


class FiltersUnionMember7(TypedDict, total=False):
    field: Required[Literal["stargazerCount"]]

    op: Required[Literal["In"]]

    value: Required[Iterable[float]]


class FiltersUnionMember8(TypedDict, total=False):
    field: Required[Literal["stargazerCount"]]

    op: Required[Literal["Gte"]]

    value: Required[float]


class FiltersUnionMember9(TypedDict, total=False):
    field: Required[Literal["stargazerCount"]]

    op: Required[Literal["Lte"]]

    value: Required[float]


class FiltersUnionMember10(TypedDict, total=False):
    field: Required[Literal["language"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUnionMember11(TypedDict, total=False):
    field: Required[Literal["language"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember12(TypedDict, total=False):
    field: Required[Literal["totalIssuesCount"]]

    op: Required[Literal["Eq"]]

    value: Required[float]


class FiltersUnionMember13(TypedDict, total=False):
    field: Required[Literal["totalIssuesCount"]]

    op: Required[Literal["In"]]

    value: Required[Iterable[float]]


class FiltersUnionMember14(TypedDict, total=False):
    field: Required[Literal["totalIssuesCount"]]

    op: Required[Literal["Gte"]]

    value: Required[float]


class FiltersUnionMember15(TypedDict, total=False):
    field: Required[Literal["totalIssuesCount"]]

    op: Required[Literal["Lte"]]

    value: Required[float]


class FiltersUnionMember16(TypedDict, total=False):
    field: Required[Literal["totalIssuesOpen"]]

    op: Required[Literal["Eq"]]

    value: Required[float]


class FiltersUnionMember17(TypedDict, total=False):
    field: Required[Literal["totalIssuesOpen"]]

    op: Required[Literal["In"]]

    value: Required[Iterable[float]]


class FiltersUnionMember18(TypedDict, total=False):
    field: Required[Literal["totalIssuesOpen"]]

    op: Required[Literal["Gte"]]

    value: Required[float]


class FiltersUnionMember19(TypedDict, total=False):
    field: Required[Literal["totalIssuesOpen"]]

    op: Required[Literal["Lte"]]

    value: Required[float]


class FiltersUnionMember20(TypedDict, total=False):
    field: Required[Literal["totalIssuesClosed"]]

    op: Required[Literal["Eq"]]

    value: Required[float]


class FiltersUnionMember21(TypedDict, total=False):
    field: Required[Literal["totalIssuesClosed"]]

    op: Required[Literal["In"]]

    value: Required[Iterable[float]]


class FiltersUnionMember22(TypedDict, total=False):
    field: Required[Literal["totalIssuesClosed"]]

    op: Required[Literal["Gte"]]

    value: Required[float]


class FiltersUnionMember23(TypedDict, total=False):
    field: Required[Literal["totalIssuesClosed"]]

    op: Required[Literal["Lte"]]

    value: Required[float]


class FiltersUnionMember24(TypedDict, total=False):
    field: Required[Literal["lastContributorLocations"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUnionMember25(TypedDict, total=False):
    field: Required[Literal["lastContributorLocations"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersRepoCompositeFilterFilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember1(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersRepoCompositeFilterFilterUnionMember2(TypedDict, total=False):
    field: Required[Literal["ownerLogin"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember3(TypedDict, total=False):
    field: Required[Literal["ownerLogin"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersRepoCompositeFilterFilterUnionMember4(TypedDict, total=False):
    field: Required[Literal["name"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember5(TypedDict, total=False):
    field: Required[Literal["name"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersRepoCompositeFilterFilterUnionMember6(TypedDict, total=False):
    field: Required[Literal["stargazerCount"]]

    op: Required[Literal["Eq"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember7(TypedDict, total=False):
    field: Required[Literal["stargazerCount"]]

    op: Required[Literal["In"]]

    value: Required[Iterable[float]]


class FiltersRepoCompositeFilterFilterUnionMember8(TypedDict, total=False):
    field: Required[Literal["stargazerCount"]]

    op: Required[Literal["Gte"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember9(TypedDict, total=False):
    field: Required[Literal["stargazerCount"]]

    op: Required[Literal["Lte"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember10(TypedDict, total=False):
    field: Required[Literal["language"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember11(TypedDict, total=False):
    field: Required[Literal["language"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersRepoCompositeFilterFilterUnionMember12(TypedDict, total=False):
    field: Required[Literal["totalIssuesCount"]]

    op: Required[Literal["Eq"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember13(TypedDict, total=False):
    field: Required[Literal["totalIssuesCount"]]

    op: Required[Literal["In"]]

    value: Required[Iterable[float]]


class FiltersRepoCompositeFilterFilterUnionMember14(TypedDict, total=False):
    field: Required[Literal["totalIssuesCount"]]

    op: Required[Literal["Gte"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember15(TypedDict, total=False):
    field: Required[Literal["totalIssuesCount"]]

    op: Required[Literal["Lte"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember16(TypedDict, total=False):
    field: Required[Literal["totalIssuesOpen"]]

    op: Required[Literal["Eq"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember17(TypedDict, total=False):
    field: Required[Literal["totalIssuesOpen"]]

    op: Required[Literal["In"]]

    value: Required[Iterable[float]]


class FiltersRepoCompositeFilterFilterUnionMember18(TypedDict, total=False):
    field: Required[Literal["totalIssuesOpen"]]

    op: Required[Literal["Gte"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember19(TypedDict, total=False):
    field: Required[Literal["totalIssuesOpen"]]

    op: Required[Literal["Lte"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember20(TypedDict, total=False):
    field: Required[Literal["totalIssuesClosed"]]

    op: Required[Literal["Eq"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember21(TypedDict, total=False):
    field: Required[Literal["totalIssuesClosed"]]

    op: Required[Literal["In"]]

    value: Required[Iterable[float]]


class FiltersRepoCompositeFilterFilterUnionMember22(TypedDict, total=False):
    field: Required[Literal["totalIssuesClosed"]]

    op: Required[Literal["Gte"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember23(TypedDict, total=False):
    field: Required[Literal["totalIssuesClosed"]]

    op: Required[Literal["Lte"]]

    value: Required[float]


class FiltersRepoCompositeFilterFilterUnionMember24(TypedDict, total=False):
    field: Required[Literal["lastContributorLocations"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersRepoCompositeFilterFilterUnionMember25(TypedDict, total=False):
    field: Required[Literal["lastContributorLocations"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


FiltersRepoCompositeFilterFilter: TypeAlias = Union[
    FiltersRepoCompositeFilterFilterUnionMember0,
    FiltersRepoCompositeFilterFilterUnionMember1,
    FiltersRepoCompositeFilterFilterUnionMember2,
    FiltersRepoCompositeFilterFilterUnionMember3,
    FiltersRepoCompositeFilterFilterUnionMember4,
    FiltersRepoCompositeFilterFilterUnionMember5,
    FiltersRepoCompositeFilterFilterUnionMember6,
    FiltersRepoCompositeFilterFilterUnionMember7,
    FiltersRepoCompositeFilterFilterUnionMember8,
    FiltersRepoCompositeFilterFilterUnionMember9,
    FiltersRepoCompositeFilterFilterUnionMember10,
    FiltersRepoCompositeFilterFilterUnionMember11,
    FiltersRepoCompositeFilterFilterUnionMember12,
    FiltersRepoCompositeFilterFilterUnionMember13,
    FiltersRepoCompositeFilterFilterUnionMember14,
    FiltersRepoCompositeFilterFilterUnionMember15,
    FiltersRepoCompositeFilterFilterUnionMember16,
    FiltersRepoCompositeFilterFilterUnionMember17,
    FiltersRepoCompositeFilterFilterUnionMember18,
    FiltersRepoCompositeFilterFilterUnionMember19,
    FiltersRepoCompositeFilterFilterUnionMember20,
    FiltersRepoCompositeFilterFilterUnionMember21,
    FiltersRepoCompositeFilterFilterUnionMember22,
    FiltersRepoCompositeFilterFilterUnionMember23,
    FiltersRepoCompositeFilterFilterUnionMember24,
    FiltersRepoCompositeFilterFilterUnionMember25,
]


class FiltersRepoCompositeFilter(TypedDict, total=False):
    filters: Required[Iterable[FiltersRepoCompositeFilterFilter]]
    """Array of field filters to combine with the logical operator"""

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine multiple filters"""


Filters: TypeAlias = Union[
    FiltersUnionMember0,
    FiltersUnionMember1,
    FiltersUnionMember2,
    FiltersUnionMember3,
    FiltersUnionMember4,
    FiltersUnionMember5,
    FiltersUnionMember6,
    FiltersUnionMember7,
    FiltersUnionMember8,
    FiltersUnionMember9,
    FiltersUnionMember10,
    FiltersUnionMember11,
    FiltersUnionMember12,
    FiltersUnionMember13,
    FiltersUnionMember14,
    FiltersUnionMember15,
    FiltersUnionMember16,
    FiltersUnionMember17,
    FiltersUnionMember18,
    FiltersUnionMember19,
    FiltersUnionMember20,
    FiltersUnionMember21,
    FiltersUnionMember22,
    FiltersUnionMember23,
    FiltersUnionMember24,
    FiltersUnionMember25,
    FiltersRepoCompositeFilter,
]
