import datetime as dt
from enum import StrEnum
from typing import Annotated, Any, List, Optional

import pytest
from pydantic import BaseModel, Field

from usajobsapi.utils import (
    _dump_by_alias,
    _is_inrange,
    _normalize_date,
    _normalize_param,
    _normalize_yn_bool,
)

# testing models
# ---


class Color(StrEnum):
    RED = "red"
    BLUE = "blue"


class QueryModel(BaseModel):
    # scalars
    a_str: Annotated[Optional[str], Field(serialization_alias="A")] = None
    a_int: Annotated[Optional[int], Field(serialization_alias="D")] = None

    # bools and enums
    a_bool: Annotated[Optional[bool], Field(serialization_alias="B")] = None
    enum_field: Annotated[Optional[Color], Field(serialization_alias="E")] = None

    # lists
    a_list_str: List[str] = Field(default_factory=list, serialization_alias="C")
    a_list_int: List[int] = Field(default_factory=list, serialization_alias="H")

    # outliers
    empty_list: List[str] = Field(default_factory=list, serialization_alias="F")
    none_field: Annotated[Optional[str], Field(serialization_alias="G")] = None


# test _normalize_date
# ---


def test_normalize_date_accepts_datetime():
    dt_value = dt.datetime(2024, 5, 17, 15, 30, 45)
    assert _normalize_date(dt_value) == dt.date(2024, 5, 17)


def test_normalize_date_accepts_date():
    date_value = dt.date(2024, 5, 17)
    assert _normalize_date(date_value) == dt.date(2024, 5, 17)


def test_normalize_date_accepts_iso_string():
    assert _normalize_date("2024-05-17") == dt.date(2024, 5, 17)


def test_normalize_date_returns_none_for_none():
    assert _normalize_date(None) is None


def test_normalize_date_rejects_bad_string():
    with pytest.raises(ValueError):
        _normalize_date("05/17/2024")


def test_normalize_date_rejects_non_date_inputs():
    with pytest.raises(TypeError):
        _normalize_date(123)  # pyright: ignore[reportArgumentType]


# test _normalize_yn_bool


def test_normalize_bool_accepts_bool():
    assert _normalize_yn_bool(True)


def test_normalize_bool_accepts_string():
    assert _normalize_yn_bool("Y")
    assert _normalize_yn_bool("YES")
    assert _normalize_yn_bool("TRUE")
    assert not _normalize_yn_bool("N")
    assert not _normalize_yn_bool("NO")
    assert not _normalize_yn_bool("FALSE")


def test_normalize_bool_returns_none_for_none():
    assert _normalize_yn_bool(None) is None


def test_normalize_bool_rejects_bad_string():
    with pytest.raises(ValueError):
        _normalize_yn_bool("indubitably")


def test_normalize_bool_rejects_non_bool_inputs():
    with pytest.raises(TypeError):
        _normalize_yn_bool(123)  # pyright: ignore[reportArgumentType]


# test _normalize_param
# ---


def test_none_returns_none():
    assert _normalize_param(None) is None


@pytest.mark.parametrize("val,expected", [(True, "True"), (False, "False")])
def test_boolean_formatting(val: bool, expected: str):
    assert _normalize_param(val) == expected


@pytest.mark.parametrize(
    "val,expected",
    [
        ("hello", "hello"),
        ("", ""),  # empty string should remain empty
        (0, "0"),  # zero preserved
        (123, "123"),
        (12.5, "12.5"),
    ],
)
def test_scalars_stringified(val: Any, expected: str):
    assert _normalize_param(val) == expected


def test_enum_stringified_to_value():
    assert _normalize_param(Color.BLUE) == "blue"


def test_list_of_strings_joined_with_semicolon():
    assert _normalize_param(["a", "b", "c"]) == "a;b;c"


def test_list_of_ints_joined_with_semicolon():
    assert _normalize_param([1, 2, 3]) == "1;2;3"


def test_list_of_enums_joined_with_semicolon():
    assert _normalize_param([Color.RED, Color.BLUE]) == "red;blue"


def test_list_of_mixed_types_joined_with_semicolon():
    mixed = [1, "x", Color.RED, True]
    assert _normalize_param(mixed) == "1;x;red;True"


def test_empty_list_returns_none():
    assert _normalize_param([]) is None


def test_tuple_is_not_joined_but_stringified():
    # Tuples are not treated as list; falls back to str(value)
    assert _normalize_param((1, 2)) == "(1, 2)"


def test_nested_list_is_stringified_element_then_joined():
    # Inner list becomes a string -> "1;[2, 3]"
    assert _normalize_param([1, [2, 3]]) == "1;[2, 3]"


# test _dump_by_alias
# ---


def test_uses_alias_names():
    m = QueryModel(a_str="hello", a_int=42)
    out = _dump_by_alias(m)
    assert out == {"A": "hello", "D": "42"}


@pytest.mark.parametrize("val,expected", [(True, "True"), (False, "False")])
def test_boolean_formatting_dump(val, expected):
    m = QueryModel(a_bool=val)
    out = _dump_by_alias(m)
    assert out == {"B": expected}


def test_list_join_semicolon_for_strings_and_ints():
    m = QueryModel(a_list_str=["x", "y", "z"], a_list_int=[1, 2, 3])
    out = _dump_by_alias(m)
    assert out["C"] == "x;y;z"
    assert out["H"] == "1;2;3"


def test_empty_list_and_none_omitted():
    m = QueryModel(a_list_str=[], none_field=None)
    out = _dump_by_alias(m)
    assert "C" not in out
    assert "G" not in out


def test_zero_and_false_are_preserved():
    m = QueryModel(a_int=0, a_bool=False)
    out = _dump_by_alias(m)
    # "0" and "False" should not be dropped
    assert out["D"] == "0"
    assert out["B"] == "False"


def test_enum_serialization():
    m = QueryModel(enum_field=Color.BLUE)
    out = _dump_by_alias(m)
    assert out == {"E": "blue"}


def test_empty_string_is_omitted():
    m = QueryModel(a_str="")
    out = _dump_by_alias(m)
    assert "A" not in out


def test_idempotent_and_no_side_effects():
    m = QueryModel(a_str="a", a_bool=True, a_list_str=["p", "q"])
    out1 = _dump_by_alias(m)
    out2 = _dump_by_alias(m)  # calling twice should produce identical results
    assert out1 == out2
    # ensure model fields weren't mutated
    assert m.a_list_str == ["p", "q"]


# test _dump_by_alias
# ---


def test_is_inrange():
    # int
    assert _is_inrange(1, 0, 2)
    assert not _is_inrange(8, 0, 2)
    # float
    assert _is_inrange(1.4, 0.5, 2.3)
    assert not _is_inrange(8.6, 0.5, 2.3)
