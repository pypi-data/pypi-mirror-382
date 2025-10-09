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
    "FiltersUserCompositeFilter",
    "FiltersUserCompositeFilterFilter",
    "FiltersUserCompositeFilterFilterUnionMember0",
    "FiltersUserCompositeFilterFilterUnionMember1",
    "FiltersUserCompositeFilterFilterUnionMember2",
    "FiltersUserCompositeFilterFilterUnionMember3",
    "FiltersUserCompositeFilterFilterUnionMember4",
    "FiltersUserCompositeFilterFilterUnionMember5",
    "FiltersUserCompositeFilterFilterUnionMember6",
    "FiltersUserCompositeFilterFilterUnionMember7",
    "FiltersUserCompositeFilterFilterUnionMember8",
    "FiltersUserCompositeFilterFilterUnionMember9",
    "FiltersUserCompositeFilterFilterUnionMember10",
    "FiltersUserCompositeFilterFilterUnionMember11",
    "FiltersUserCompositeFilterFilterUnionMember12",
    "FiltersUserCompositeFilterFilterUnionMember13",
    "FiltersUserCompositeFilterFilterUnionMember14",
    "FiltersUserCompositeFilterFilterUnionMember15",
]


class SearchUserSearchParams(TypedDict, total=False):
    query: Required[str]
    """Full-text search query across user fields.

    Searches: login, displayName, bio, company, location, emails, resolvedCountry,
    resolvedState, resolvedCity (with login weighted 2x)
    """

    filters: Optional[Filters]
    """Optional filters for narrowing search results.

    Supports filtering on: githubId, login, company, location, emails,
    resolvedCountry, resolvedState, resolvedCity.

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


class FiltersUnionMember0(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUnionMember1(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember2(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUnionMember3(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember4(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUnionMember5(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember6(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUnionMember7(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember8(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUnionMember9(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember10(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUnionMember11(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember12(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUnionMember13(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUnionMember14(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUnionMember15(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUserCompositeFilterFilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember1(TypedDict, total=False):
    field: Required[Literal["githubId"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUserCompositeFilterFilterUnionMember2(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember3(TypedDict, total=False):
    field: Required[Literal["login"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUserCompositeFilterFilterUnionMember4(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember5(TypedDict, total=False):
    field: Required[Literal["company"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUserCompositeFilterFilterUnionMember6(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember7(TypedDict, total=False):
    field: Required[Literal["location"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUserCompositeFilterFilterUnionMember8(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember9(TypedDict, total=False):
    field: Required[Literal["emails"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUserCompositeFilterFilterUnionMember10(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember11(TypedDict, total=False):
    field: Required[Literal["resolvedCountry"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUserCompositeFilterFilterUnionMember12(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember13(TypedDict, total=False):
    field: Required[Literal["resolvedState"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


class FiltersUserCompositeFilterFilterUnionMember14(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["Eq"]]

    value: Required[str]


class FiltersUserCompositeFilterFilterUnionMember15(TypedDict, total=False):
    field: Required[Literal["resolvedCity"]]

    op: Required[Literal["In"]]

    value: Required[SequenceNotStr[str]]


FiltersUserCompositeFilterFilter: TypeAlias = Union[
    FiltersUserCompositeFilterFilterUnionMember0,
    FiltersUserCompositeFilterFilterUnionMember1,
    FiltersUserCompositeFilterFilterUnionMember2,
    FiltersUserCompositeFilterFilterUnionMember3,
    FiltersUserCompositeFilterFilterUnionMember4,
    FiltersUserCompositeFilterFilterUnionMember5,
    FiltersUserCompositeFilterFilterUnionMember6,
    FiltersUserCompositeFilterFilterUnionMember7,
    FiltersUserCompositeFilterFilterUnionMember8,
    FiltersUserCompositeFilterFilterUnionMember9,
    FiltersUserCompositeFilterFilterUnionMember10,
    FiltersUserCompositeFilterFilterUnionMember11,
    FiltersUserCompositeFilterFilterUnionMember12,
    FiltersUserCompositeFilterFilterUnionMember13,
    FiltersUserCompositeFilterFilterUnionMember14,
    FiltersUserCompositeFilterFilterUnionMember15,
]


class FiltersUserCompositeFilter(TypedDict, total=False):
    filters: Required[Iterable[FiltersUserCompositeFilterFilter]]
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
    FiltersUserCompositeFilter,
]
