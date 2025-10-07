# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = [
    "SearchUserSearchParams",
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
    "FiltersUnionMember3",
    "FiltersUnionMember3UnionMember0",
    "FiltersUnionMember3UnionMember1",
    "FiltersUnionMember4",
    "FiltersUnionMember4UnionMember0",
    "FiltersUnionMember4UnionMember1",
    "FiltersUnionMember5",
    "FiltersUnionMember5UnionMember0",
    "FiltersUnionMember5UnionMember1",
    "FiltersUnionMember6",
    "FiltersUnionMember6UnionMember0",
    "FiltersUnionMember6UnionMember1",
    "FiltersUnionMember7",
    "FiltersUnionMember7FilterUnionMember0",
    "FiltersUnionMember7FilterUnionMember0UnionMember0",
    "FiltersUnionMember7FilterUnionMember0UnionMember1",
    "FiltersUnionMember7FilterUnionMember1",
    "FiltersUnionMember7FilterUnionMember1UnionMember0",
    "FiltersUnionMember7FilterUnionMember1UnionMember1",
    "FiltersUnionMember7FilterUnionMember2",
    "FiltersUnionMember7FilterUnionMember2UnionMember0",
    "FiltersUnionMember7FilterUnionMember2UnionMember1",
    "FiltersUnionMember7FilterUnionMember3",
    "FiltersUnionMember7FilterUnionMember3UnionMember0",
    "FiltersUnionMember7FilterUnionMember3UnionMember1",
    "FiltersUnionMember7FilterUnionMember4",
    "FiltersUnionMember7FilterUnionMember4UnionMember0",
    "FiltersUnionMember7FilterUnionMember4UnionMember1",
    "FiltersUnionMember7FilterUnionMember5",
    "FiltersUnionMember7FilterUnionMember5UnionMember0",
    "FiltersUnionMember7FilterUnionMember5UnionMember1",
    "FiltersUnionMember7FilterUnionMember6",
    "FiltersUnionMember7FilterUnionMember6UnionMember0",
    "FiltersUnionMember7FilterUnionMember6UnionMember1",
]


class SearchUserSearchParams(TypedDict, total=False):
    query: Required[str]
    """Full-text search query across user fields.

    Searches: login, displayName, bio, company, location, emails, resolvedCountry,
    resolvedState, resolvedCity (with login weighted 2x)
    """

    filters: Optional[Filters]
    """Optional filters for narrowing search results.

    Supports filtering on: login, company, location, emails, resolvedCountry,
    resolvedState, resolvedCity.

    Full-text searchable fields (automatically searched): login, displayName, bio,
    company, location, emails, resolvedCountry, resolvedState, resolvedCity.

    Filter structure:

    - Field filters: { field: "fieldName", op: "Eq"|"In", value: string|string[] }
    - Composite filters: { op: "And"|"Or", filters: [...] }

    Supported operators:

    - String fields: Eq (exact match), In (one of array)
    - Use And/Or to combine multiple filters
    """

    max_results: Annotated[int, PropertyInfo(alias="maxResults")]
    """Maximum number of results to return (default: 100, max: 1000)"""


class FiltersUnionMember0UnionMember0(TypedDict, total=False):
    op: Required[Literal["Eq"]]

    value: Required[str]

    field: Literal["login"]


class FiltersUnionMember0UnionMember1(TypedDict, total=False):
    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]

    field: Literal["login"]


FiltersUnionMember0: TypeAlias = Union[FiltersUnionMember0UnionMember0, FiltersUnionMember0UnionMember1]


class FiltersUnionMember1UnionMember0(TypedDict, total=False):
    op: Required[Literal["Eq"]]

    value: Required[str]

    field: Literal["company"]


class FiltersUnionMember1UnionMember1(TypedDict, total=False):
    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]

    field: Literal["company"]


FiltersUnionMember1: TypeAlias = Union[FiltersUnionMember1UnionMember0, FiltersUnionMember1UnionMember1]


class FiltersUnionMember2UnionMember0(TypedDict, total=False):
    op: Required[Literal["Eq"]]

    value: Required[str]

    field: Literal["location"]


class FiltersUnionMember2UnionMember1(TypedDict, total=False):
    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]

    field: Literal["location"]


FiltersUnionMember2: TypeAlias = Union[FiltersUnionMember2UnionMember0, FiltersUnionMember2UnionMember1]


class FiltersUnionMember3UnionMember0(TypedDict, total=False):
    op: Required[Literal["Eq"]]

    value: Required[str]

    field: Literal["emails"]


class FiltersUnionMember3UnionMember1(TypedDict, total=False):
    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]

    field: Literal["emails"]


FiltersUnionMember3: TypeAlias = Union[FiltersUnionMember3UnionMember0, FiltersUnionMember3UnionMember1]


class FiltersUnionMember4UnionMember0(TypedDict, total=False):
    op: Required[Literal["Eq"]]

    value: Required[str]

    field: Literal["resolvedCountry"]


class FiltersUnionMember4UnionMember1(TypedDict, total=False):
    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]

    field: Literal["resolvedCountry"]


FiltersUnionMember4: TypeAlias = Union[FiltersUnionMember4UnionMember0, FiltersUnionMember4UnionMember1]


class FiltersUnionMember5UnionMember0(TypedDict, total=False):
    op: Required[Literal["Eq"]]

    value: Required[str]

    field: Literal["resolvedState"]


class FiltersUnionMember5UnionMember1(TypedDict, total=False):
    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]

    field: Literal["resolvedState"]


FiltersUnionMember5: TypeAlias = Union[FiltersUnionMember5UnionMember0, FiltersUnionMember5UnionMember1]


class FiltersUnionMember6UnionMember0(TypedDict, total=False):
    op: Required[Literal["Eq"]]

    value: Required[str]

    field: Literal["resolvedCity"]


class FiltersUnionMember6UnionMember1(TypedDict, total=False):
    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]

    field: Literal["resolvedCity"]


FiltersUnionMember6: TypeAlias = Union[FiltersUnionMember6UnionMember0, FiltersUnionMember6UnionMember1]


class FiltersUnionMember7FilterUnionMember0UnionMember0(TypedDict, total=False):
    op: Required[Literal["Eq"]]

    value: Required[str]

    field: Literal["login"]


class FiltersUnionMember7FilterUnionMember0UnionMember1(TypedDict, total=False):
    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]

    field: Literal["login"]


FiltersUnionMember7FilterUnionMember0: TypeAlias = Union[
    FiltersUnionMember7FilterUnionMember0UnionMember0, FiltersUnionMember7FilterUnionMember0UnionMember1
]


class FiltersUnionMember7FilterUnionMember1UnionMember0(TypedDict, total=False):
    op: Required[Literal["Eq"]]

    value: Required[str]

    field: Literal["company"]


class FiltersUnionMember7FilterUnionMember1UnionMember1(TypedDict, total=False):
    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]

    field: Literal["company"]


FiltersUnionMember7FilterUnionMember1: TypeAlias = Union[
    FiltersUnionMember7FilterUnionMember1UnionMember0, FiltersUnionMember7FilterUnionMember1UnionMember1
]


class FiltersUnionMember7FilterUnionMember2UnionMember0(TypedDict, total=False):
    op: Required[Literal["Eq"]]

    value: Required[str]

    field: Literal["location"]


class FiltersUnionMember7FilterUnionMember2UnionMember1(TypedDict, total=False):
    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]

    field: Literal["location"]


FiltersUnionMember7FilterUnionMember2: TypeAlias = Union[
    FiltersUnionMember7FilterUnionMember2UnionMember0, FiltersUnionMember7FilterUnionMember2UnionMember1
]


class FiltersUnionMember7FilterUnionMember3UnionMember0(TypedDict, total=False):
    op: Required[Literal["Eq"]]

    value: Required[str]

    field: Literal["emails"]


class FiltersUnionMember7FilterUnionMember3UnionMember1(TypedDict, total=False):
    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]

    field: Literal["emails"]


FiltersUnionMember7FilterUnionMember3: TypeAlias = Union[
    FiltersUnionMember7FilterUnionMember3UnionMember0, FiltersUnionMember7FilterUnionMember3UnionMember1
]


class FiltersUnionMember7FilterUnionMember4UnionMember0(TypedDict, total=False):
    op: Required[Literal["Eq"]]

    value: Required[str]

    field: Literal["resolvedCountry"]


class FiltersUnionMember7FilterUnionMember4UnionMember1(TypedDict, total=False):
    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]

    field: Literal["resolvedCountry"]


FiltersUnionMember7FilterUnionMember4: TypeAlias = Union[
    FiltersUnionMember7FilterUnionMember4UnionMember0, FiltersUnionMember7FilterUnionMember4UnionMember1
]


class FiltersUnionMember7FilterUnionMember5UnionMember0(TypedDict, total=False):
    op: Required[Literal["Eq"]]

    value: Required[str]

    field: Literal["resolvedState"]


class FiltersUnionMember7FilterUnionMember5UnionMember1(TypedDict, total=False):
    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]

    field: Literal["resolvedState"]


FiltersUnionMember7FilterUnionMember5: TypeAlias = Union[
    FiltersUnionMember7FilterUnionMember5UnionMember0, FiltersUnionMember7FilterUnionMember5UnionMember1
]


class FiltersUnionMember7FilterUnionMember6UnionMember0(TypedDict, total=False):
    op: Required[Literal["Eq"]]

    value: Required[str]

    field: Literal["resolvedCity"]


class FiltersUnionMember7FilterUnionMember6UnionMember1(TypedDict, total=False):
    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]

    field: Literal["resolvedCity"]


FiltersUnionMember7FilterUnionMember6: TypeAlias = Union[
    FiltersUnionMember7FilterUnionMember6UnionMember0, FiltersUnionMember7FilterUnionMember6UnionMember1
]


class FiltersUnionMember7(TypedDict, total=False):
    filters: Required[
        Iterable[
            Union[
                FiltersUnionMember7FilterUnionMember0,
                FiltersUnionMember7FilterUnionMember1,
                FiltersUnionMember7FilterUnionMember2,
                FiltersUnionMember7FilterUnionMember3,
                FiltersUnionMember7FilterUnionMember4,
                FiltersUnionMember7FilterUnionMember5,
                FiltersUnionMember7FilterUnionMember6,
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
]
