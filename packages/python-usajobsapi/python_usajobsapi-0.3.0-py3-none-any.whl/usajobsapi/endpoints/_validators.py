from typing import List

from usajobsapi.utils import _is_inrange


def isvalid_pay_grade(value: str):
    if value in ("01", "02", "03", "04", "05", "06", "07", "08", "09", "10"):
        return value
    if value in ("1", "2", "3", "4", "5", "6", "7", "8", "9"):
        return f"0{value}"
    raise ValueError(f"{value} must be a GS pay grade (01-15)")


def isvalid_pos_sensitivity(value: List[int]):
    if all(_is_inrange(x, 1, 7) for x in value):
        return value
    raise ValueError(
        "Acceptable values for Position Sensitivity and Risk parameter are 1 through 7."
    )
