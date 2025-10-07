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
    "FiltersUnionMember0UnionMember0",
    "FiltersUnionMember0UnionMember1",
    "FiltersUnionMember1",
    "FiltersUnionMember1UnionMember0",
    "FiltersUnionMember1UnionMember1",
    "FiltersUnionMember2",
    "FiltersUnionMember2UnionMember0",
    "FiltersUnionMember2UnionMember1",
    "FiltersUnionMember2UnionMember2",
    "FiltersUnionMember2UnionMember3",
    "FiltersUnionMember3",
    "FiltersUnionMember3UnionMember0",
    "FiltersUnionMember3UnionMember1",
    "FiltersUnionMember4",
    "FiltersUnionMember4UnionMember0",
    "FiltersUnionMember4UnionMember1",
    "FiltersUnionMember4UnionMember2",
    "FiltersUnionMember4UnionMember3",
    "FiltersUnionMember5",
    "FiltersUnionMember5UnionMember0",
    "FiltersUnionMember5UnionMember1",
    "FiltersUnionMember5UnionMember2",
    "FiltersUnionMember5UnionMember3",
    "FiltersUnionMember6",
    "FiltersUnionMember6UnionMember0",
    "FiltersUnionMember6UnionMember1",
    "FiltersUnionMember6UnionMember2",
    "FiltersUnionMember6UnionMember3",
    "FiltersUnionMember7",
    "FiltersUnionMember7UnionMember0",
    "FiltersUnionMember7UnionMember1",
    "FiltersUnionMember8",
    "FiltersUnionMember8FilterUnionMember0",
    "FiltersUnionMember8FilterUnionMember0UnionMember0",
    "FiltersUnionMember8FilterUnionMember0UnionMember1",
    "FiltersUnionMember8FilterUnionMember1",
    "FiltersUnionMember8FilterUnionMember1UnionMember0",
    "FiltersUnionMember8FilterUnionMember1UnionMember1",
    "FiltersUnionMember8FilterUnionMember2",
    "FiltersUnionMember8FilterUnionMember2UnionMember0",
    "FiltersUnionMember8FilterUnionMember2UnionMember1",
    "FiltersUnionMember8FilterUnionMember2UnionMember2",
    "FiltersUnionMember8FilterUnionMember2UnionMember3",
    "FiltersUnionMember8FilterUnionMember3",
    "FiltersUnionMember8FilterUnionMember3UnionMember0",
    "FiltersUnionMember8FilterUnionMember3UnionMember1",
    "FiltersUnionMember8FilterUnionMember4",
    "FiltersUnionMember8FilterUnionMember4UnionMember0",
    "FiltersUnionMember8FilterUnionMember4UnionMember1",
    "FiltersUnionMember8FilterUnionMember4UnionMember2",
    "FiltersUnionMember8FilterUnionMember4UnionMember3",
    "FiltersUnionMember8FilterUnionMember5",
    "FiltersUnionMember8FilterUnionMember5UnionMember0",
    "FiltersUnionMember8FilterUnionMember5UnionMember1",
    "FiltersUnionMember8FilterUnionMember5UnionMember2",
    "FiltersUnionMember8FilterUnionMember5UnionMember3",
    "FiltersUnionMember8FilterUnionMember6",
    "FiltersUnionMember8FilterUnionMember6UnionMember0",
    "FiltersUnionMember8FilterUnionMember6UnionMember1",
    "FiltersUnionMember8FilterUnionMember6UnionMember2",
    "FiltersUnionMember8FilterUnionMember6UnionMember3",
    "FiltersUnionMember8FilterUnionMember7",
    "FiltersUnionMember8FilterUnionMember7UnionMember0",
    "FiltersUnionMember8FilterUnionMember7UnionMember1",
]


class SearchRepoSearchParams(TypedDict, total=False):
    query: Required[str]
    """
    Natural language search query for semantic search across repository README and
    description using vector embeddings
    """

    filters: Optional[Filters]
    """Optional filters for narrowing search results.

    Supports filtering on: ownerLogin, name, stargazerCount, language,
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


class FiltersUnionMember0UnionMember0(TypedDict, total=False):
    op: Required[Literal["Eq"]]

    value: Required[str]

    field: Literal["ownerLogin"]


class FiltersUnionMember0UnionMember1(TypedDict, total=False):
    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]

    field: Literal["ownerLogin"]


FiltersUnionMember0: TypeAlias = Union[FiltersUnionMember0UnionMember0, FiltersUnionMember0UnionMember1]


class FiltersUnionMember1UnionMember0(TypedDict, total=False):
    op: Required[Literal["Eq"]]

    value: Required[str]

    field: Literal["name"]


class FiltersUnionMember1UnionMember1(TypedDict, total=False):
    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]

    field: Literal["name"]


FiltersUnionMember1: TypeAlias = Union[FiltersUnionMember1UnionMember0, FiltersUnionMember1UnionMember1]


class FiltersUnionMember2UnionMember0(TypedDict, total=False):
    op: Required[Literal["Eq"]]

    value: Required[float]

    field: Literal["stargazerCount"]


class FiltersUnionMember2UnionMember1(TypedDict, total=False):
    op: Required[Literal["In"]]

    value: Required[Iterable[float]]

    field: Literal["stargazerCount"]


class FiltersUnionMember2UnionMember2(TypedDict, total=False):
    op: Required[Literal["Gte"]]

    value: Required[float]

    field: Literal["stargazerCount"]


class FiltersUnionMember2UnionMember3(TypedDict, total=False):
    op: Required[Literal["Lte"]]

    value: Required[float]

    field: Literal["stargazerCount"]


FiltersUnionMember2: TypeAlias = Union[
    FiltersUnionMember2UnionMember0,
    FiltersUnionMember2UnionMember1,
    FiltersUnionMember2UnionMember2,
    FiltersUnionMember2UnionMember3,
]


class FiltersUnionMember3UnionMember0(TypedDict, total=False):
    op: Required[Literal["Eq"]]

    value: Required[str]

    field: Literal["language"]


class FiltersUnionMember3UnionMember1(TypedDict, total=False):
    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]

    field: Literal["language"]


FiltersUnionMember3: TypeAlias = Union[FiltersUnionMember3UnionMember0, FiltersUnionMember3UnionMember1]


class FiltersUnionMember4UnionMember0(TypedDict, total=False):
    op: Required[Literal["Eq"]]

    value: Required[float]

    field: Literal["totalIssuesCount"]


class FiltersUnionMember4UnionMember1(TypedDict, total=False):
    op: Required[Literal["In"]]

    value: Required[Iterable[float]]

    field: Literal["totalIssuesCount"]


class FiltersUnionMember4UnionMember2(TypedDict, total=False):
    op: Required[Literal["Gte"]]

    value: Required[float]

    field: Literal["totalIssuesCount"]


class FiltersUnionMember4UnionMember3(TypedDict, total=False):
    op: Required[Literal["Lte"]]

    value: Required[float]

    field: Literal["totalIssuesCount"]


FiltersUnionMember4: TypeAlias = Union[
    FiltersUnionMember4UnionMember0,
    FiltersUnionMember4UnionMember1,
    FiltersUnionMember4UnionMember2,
    FiltersUnionMember4UnionMember3,
]


class FiltersUnionMember5UnionMember0(TypedDict, total=False):
    op: Required[Literal["Eq"]]

    value: Required[float]

    field: Literal["totalIssuesOpen"]


class FiltersUnionMember5UnionMember1(TypedDict, total=False):
    op: Required[Literal["In"]]

    value: Required[Iterable[float]]

    field: Literal["totalIssuesOpen"]


class FiltersUnionMember5UnionMember2(TypedDict, total=False):
    op: Required[Literal["Gte"]]

    value: Required[float]

    field: Literal["totalIssuesOpen"]


class FiltersUnionMember5UnionMember3(TypedDict, total=False):
    op: Required[Literal["Lte"]]

    value: Required[float]

    field: Literal["totalIssuesOpen"]


FiltersUnionMember5: TypeAlias = Union[
    FiltersUnionMember5UnionMember0,
    FiltersUnionMember5UnionMember1,
    FiltersUnionMember5UnionMember2,
    FiltersUnionMember5UnionMember3,
]


class FiltersUnionMember6UnionMember0(TypedDict, total=False):
    op: Required[Literal["Eq"]]

    value: Required[float]

    field: Literal["totalIssuesClosed"]


class FiltersUnionMember6UnionMember1(TypedDict, total=False):
    op: Required[Literal["In"]]

    value: Required[Iterable[float]]

    field: Literal["totalIssuesClosed"]


class FiltersUnionMember6UnionMember2(TypedDict, total=False):
    op: Required[Literal["Gte"]]

    value: Required[float]

    field: Literal["totalIssuesClosed"]


class FiltersUnionMember6UnionMember3(TypedDict, total=False):
    op: Required[Literal["Lte"]]

    value: Required[float]

    field: Literal["totalIssuesClosed"]


FiltersUnionMember6: TypeAlias = Union[
    FiltersUnionMember6UnionMember0,
    FiltersUnionMember6UnionMember1,
    FiltersUnionMember6UnionMember2,
    FiltersUnionMember6UnionMember3,
]


class FiltersUnionMember7UnionMember0(TypedDict, total=False):
    op: Required[Literal["Eq"]]

    value: Required[str]

    field: Literal["lastContributorLocations"]


class FiltersUnionMember7UnionMember1(TypedDict, total=False):
    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]

    field: Literal["lastContributorLocations"]


FiltersUnionMember7: TypeAlias = Union[FiltersUnionMember7UnionMember0, FiltersUnionMember7UnionMember1]


class FiltersUnionMember8FilterUnionMember0UnionMember0(TypedDict, total=False):
    op: Required[Literal["Eq"]]

    value: Required[str]

    field: Literal["ownerLogin"]


class FiltersUnionMember8FilterUnionMember0UnionMember1(TypedDict, total=False):
    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]

    field: Literal["ownerLogin"]


FiltersUnionMember8FilterUnionMember0: TypeAlias = Union[
    FiltersUnionMember8FilterUnionMember0UnionMember0, FiltersUnionMember8FilterUnionMember0UnionMember1
]


class FiltersUnionMember8FilterUnionMember1UnionMember0(TypedDict, total=False):
    op: Required[Literal["Eq"]]

    value: Required[str]

    field: Literal["name"]


class FiltersUnionMember8FilterUnionMember1UnionMember1(TypedDict, total=False):
    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]

    field: Literal["name"]


FiltersUnionMember8FilterUnionMember1: TypeAlias = Union[
    FiltersUnionMember8FilterUnionMember1UnionMember0, FiltersUnionMember8FilterUnionMember1UnionMember1
]


class FiltersUnionMember8FilterUnionMember2UnionMember0(TypedDict, total=False):
    op: Required[Literal["Eq"]]

    value: Required[float]

    field: Literal["stargazerCount"]


class FiltersUnionMember8FilterUnionMember2UnionMember1(TypedDict, total=False):
    op: Required[Literal["In"]]

    value: Required[Iterable[float]]

    field: Literal["stargazerCount"]


class FiltersUnionMember8FilterUnionMember2UnionMember2(TypedDict, total=False):
    op: Required[Literal["Gte"]]

    value: Required[float]

    field: Literal["stargazerCount"]


class FiltersUnionMember8FilterUnionMember2UnionMember3(TypedDict, total=False):
    op: Required[Literal["Lte"]]

    value: Required[float]

    field: Literal["stargazerCount"]


FiltersUnionMember8FilterUnionMember2: TypeAlias = Union[
    FiltersUnionMember8FilterUnionMember2UnionMember0,
    FiltersUnionMember8FilterUnionMember2UnionMember1,
    FiltersUnionMember8FilterUnionMember2UnionMember2,
    FiltersUnionMember8FilterUnionMember2UnionMember3,
]


class FiltersUnionMember8FilterUnionMember3UnionMember0(TypedDict, total=False):
    op: Required[Literal["Eq"]]

    value: Required[str]

    field: Literal["language"]


class FiltersUnionMember8FilterUnionMember3UnionMember1(TypedDict, total=False):
    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]

    field: Literal["language"]


FiltersUnionMember8FilterUnionMember3: TypeAlias = Union[
    FiltersUnionMember8FilterUnionMember3UnionMember0, FiltersUnionMember8FilterUnionMember3UnionMember1
]


class FiltersUnionMember8FilterUnionMember4UnionMember0(TypedDict, total=False):
    op: Required[Literal["Eq"]]

    value: Required[float]

    field: Literal["totalIssuesCount"]


class FiltersUnionMember8FilterUnionMember4UnionMember1(TypedDict, total=False):
    op: Required[Literal["In"]]

    value: Required[Iterable[float]]

    field: Literal["totalIssuesCount"]


class FiltersUnionMember8FilterUnionMember4UnionMember2(TypedDict, total=False):
    op: Required[Literal["Gte"]]

    value: Required[float]

    field: Literal["totalIssuesCount"]


class FiltersUnionMember8FilterUnionMember4UnionMember3(TypedDict, total=False):
    op: Required[Literal["Lte"]]

    value: Required[float]

    field: Literal["totalIssuesCount"]


FiltersUnionMember8FilterUnionMember4: TypeAlias = Union[
    FiltersUnionMember8FilterUnionMember4UnionMember0,
    FiltersUnionMember8FilterUnionMember4UnionMember1,
    FiltersUnionMember8FilterUnionMember4UnionMember2,
    FiltersUnionMember8FilterUnionMember4UnionMember3,
]


class FiltersUnionMember8FilterUnionMember5UnionMember0(TypedDict, total=False):
    op: Required[Literal["Eq"]]

    value: Required[float]

    field: Literal["totalIssuesOpen"]


class FiltersUnionMember8FilterUnionMember5UnionMember1(TypedDict, total=False):
    op: Required[Literal["In"]]

    value: Required[Iterable[float]]

    field: Literal["totalIssuesOpen"]


class FiltersUnionMember8FilterUnionMember5UnionMember2(TypedDict, total=False):
    op: Required[Literal["Gte"]]

    value: Required[float]

    field: Literal["totalIssuesOpen"]


class FiltersUnionMember8FilterUnionMember5UnionMember3(TypedDict, total=False):
    op: Required[Literal["Lte"]]

    value: Required[float]

    field: Literal["totalIssuesOpen"]


FiltersUnionMember8FilterUnionMember5: TypeAlias = Union[
    FiltersUnionMember8FilterUnionMember5UnionMember0,
    FiltersUnionMember8FilterUnionMember5UnionMember1,
    FiltersUnionMember8FilterUnionMember5UnionMember2,
    FiltersUnionMember8FilterUnionMember5UnionMember3,
]


class FiltersUnionMember8FilterUnionMember6UnionMember0(TypedDict, total=False):
    op: Required[Literal["Eq"]]

    value: Required[float]

    field: Literal["totalIssuesClosed"]


class FiltersUnionMember8FilterUnionMember6UnionMember1(TypedDict, total=False):
    op: Required[Literal["In"]]

    value: Required[Iterable[float]]

    field: Literal["totalIssuesClosed"]


class FiltersUnionMember8FilterUnionMember6UnionMember2(TypedDict, total=False):
    op: Required[Literal["Gte"]]

    value: Required[float]

    field: Literal["totalIssuesClosed"]


class FiltersUnionMember8FilterUnionMember6UnionMember3(TypedDict, total=False):
    op: Required[Literal["Lte"]]

    value: Required[float]

    field: Literal["totalIssuesClosed"]


FiltersUnionMember8FilterUnionMember6: TypeAlias = Union[
    FiltersUnionMember8FilterUnionMember6UnionMember0,
    FiltersUnionMember8FilterUnionMember6UnionMember1,
    FiltersUnionMember8FilterUnionMember6UnionMember2,
    FiltersUnionMember8FilterUnionMember6UnionMember3,
]


class FiltersUnionMember8FilterUnionMember7UnionMember0(TypedDict, total=False):
    op: Required[Literal["Eq"]]

    value: Required[str]

    field: Literal["lastContributorLocations"]


class FiltersUnionMember8FilterUnionMember7UnionMember1(TypedDict, total=False):
    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]

    field: Literal["lastContributorLocations"]


FiltersUnionMember8FilterUnionMember7: TypeAlias = Union[
    FiltersUnionMember8FilterUnionMember7UnionMember0, FiltersUnionMember8FilterUnionMember7UnionMember1
]


class FiltersUnionMember8(TypedDict, total=False):
    filters: Required[
        Iterable[
            Union[
                FiltersUnionMember8FilterUnionMember0,
                FiltersUnionMember8FilterUnionMember1,
                FiltersUnionMember8FilterUnionMember2,
                FiltersUnionMember8FilterUnionMember3,
                FiltersUnionMember8FilterUnionMember4,
                FiltersUnionMember8FilterUnionMember5,
                FiltersUnionMember8FilterUnionMember6,
                FiltersUnionMember8FilterUnionMember7,
            ]
        ]
    ]
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
]
