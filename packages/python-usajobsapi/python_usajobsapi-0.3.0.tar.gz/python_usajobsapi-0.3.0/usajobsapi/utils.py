"""
Helper utility functions.

Shared helpers keep endpoint payloads consistent and ergonomic. These utilities handle normalization, serialization, and data validation used throughout the client and endpoint models.
"""

import datetime as dt
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel


def _normalize_date(value: None | dt.datetime | dt.date | str) -> Optional[dt.date]:
    """Normalize to `datetime.date`."""

    if value is None:
        return None
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    if isinstance(value, str):
        try:
            return dt.date.fromisoformat(value)
        except ValueError as exc:
            msg = "Value must be an ISO 8601 date string (YYYY-MM-DD)"
            raise ValueError(msg) from exc
    msg = "Expected value type of datetime, date, or ISO date string"
    raise TypeError(msg)


def _normalize_yn_bool(value: None | bool | str) -> Optional[bool]:
    """Normalize `"Y"`/`"N"` to `bool`."""

    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().upper()
        if normalized in {"Y", "YES", "TRUE", "1"}:
            return True
        if normalized in {"N", "NO", "FALSE", "0"}:
            return False
        raise ValueError("Value must be a Y/YES/TRUE/1 or N/NO/FALSE/0 string")
    raise TypeError("Expected value type of bool or Y/N string")


def _normalize_param(value: Any) -> Optional[str]:
    """Normalize query parameters to the format expected by USAJOBS.

    :param value: Query parameter to normalize
    :type value: Any
    :return: Query parameter normalized for the USAJOBS REST API.
    :rtype: Optional[str]
    """
    if value is None:
        # None -> omit
        return None
    if isinstance(value, bool):
        # bools -> 'True'/'False'
        return "True" if value else "False"
    if isinstance(value, Enum):
        # enums -> use the serialized value
        return str(value.value)
    if isinstance(value, list):
        # lists -> ';'
        if not value:
            return None
        normalized_items = []
        for item in value:
            if isinstance(item, bool):
                normalized_items.append("True" if item else "False")
            elif isinstance(item, Enum):
                normalized_items.append(str(item.value))
            else:
                normalized_items.append(str(item))
        return ";".join(normalized_items)
    # Everything else as a string
    return str(value)


def _dump_by_alias(model: BaseModel) -> Dict[str, str]:
    """Dump a Pydantic model to a query-param dict using the model's field aliases and USAJOBS formatting rules (lists + bools).

    :param model: Pydantic model instance to export using field aliases
    :type model: BaseModel
    :return: Mapping of alias names to normalized parameter values
    :rtype: Dict[str, str]
    """
    # Use the API's wire names and drop `None`s
    raw = model.model_dump(by_alias=True, exclude_none=True, mode="json")

    # Normalize values
    out: Dict[str, str] = {}
    for k, v in raw.items():
        norm_val = _normalize_param(v)
        if norm_val:
            out[k] = norm_val
    return out


def _is_inrange(n: int | float, lower: int | float, upper: int | float):
    """A simple utility function that checks a given value is within the given closed interval.

    A closed interval [a, b] represents the set of all real numbers greater or equal to a and less or equal to b.

    :param n: Value to check
    :type n: int
    :param lower: Lower bound of the interval
    :type lower: int
    :param upper: Upper bound of the interval
    :type upper: int
    :return: `True` if the value falls inside the closed interval `[lower, upper]`
    :rtype: bool
    """
    return n >= lower and n <= upper
