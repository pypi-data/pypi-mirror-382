"""Unit tests for HistoricJoaEndpoint."""

import datetime as dt

import pytest

from usajobsapi.endpoints.historicjoa import HistoricJoaEndpoint


def test_params_to_params_serializes_aliases(historicjoa_params_kwargs) -> None:
    """Validate Params.to_params uses USAJOBS aliases and formatting."""

    params = HistoricJoaEndpoint.Params(**historicjoa_params_kwargs)

    assert isinstance(params.start_position_open_date, dt.date)
    assert isinstance(params.end_position_open_date, dt.date)
    assert isinstance(params.start_position_close_date, dt.date)
    assert isinstance(params.end_position_close_date, dt.date)

    serialized = params.to_params()

    expected = {
        "HiringAgencyCodes": "AGENCY1",
        "HiringDepartmentCodes": "DEPT1",
        "PositionSeries": "2210",
        "AnnouncementNumbers": "23-ABC",
        "USAJOBSControlNumbers": "1234567",
        "StartPositionOpenDate": "2020-01-01",
        "EndPositionOpenDate": "2020-12-31",
        "StartPositionCloseDate": "2021-01-01",
        "EndPositionCloseDate": "2021-12-31",
        "continuationToken": "token123",
    }

    assert serialized == expected


def test_params_to_params_accepts_datetime_for_start_open_date(
    historicjoa_params_kwargs,
) -> None:
    """Ensure start_position_open_date accepts datetime instances."""

    kwargs = historicjoa_params_kwargs.copy()
    kwargs["start_position_open_date"] = dt.datetime(2020, 1, 1, 8, 30)

    params = HistoricJoaEndpoint.Params(**kwargs)

    assert isinstance(params.start_position_open_date, dt.date)

    serialized = params.to_params()

    assert serialized["StartPositionOpenDate"] == "2020-01-01"


def test_params_to_params_rejects_time_for_start_open_date(
    historicjoa_params_kwargs,
) -> None:
    """Ensure start_position_open_date rejects time-only values."""

    kwargs = historicjoa_params_kwargs.copy()
    kwargs["start_position_open_date"] = dt.time(8, 45, 15)

    with pytest.raises(TypeError):
        HistoricJoaEndpoint.Params(**kwargs)


def test_params_to_params_rejects_bad_string_format(historicjoa_params_kwargs) -> None:
    """Ensure invalid date strings are rejected with a ValueError."""

    kwargs = historicjoa_params_kwargs.copy()
    kwargs["start_position_open_date"] = "01-01-2020"

    with pytest.raises(ValueError):
        HistoricJoaEndpoint.Params(**kwargs)


def test_params_to_params_omits_none_fields(historicjoa_params_kwargs) -> None:
    """Ensure Params.to_params excludes unset or None-valued fields."""

    kwargs = historicjoa_params_kwargs.copy()
    for optional in (
        "hiring_department_codes",
        "announcement_numbers",
        "continuation_token",
    ):
        kwargs[optional] = None

    params = HistoricJoaEndpoint.Params(**kwargs)

    assert params.start_position_open_date is None or isinstance(
        params.start_position_open_date, dt.date
    )

    serialized = params.to_params()

    assert "HiringDepartmentCodes" not in serialized
    assert "AnnouncementNumbers" not in serialized
    assert "continuationToken" not in serialized
    assert serialized["HiringAgencyCodes"] == "AGENCY1"


def test_item_model_parses_response_payload(historicjoa_response_payload) -> None:
    """Confirm Item model accepts serialized payload dictionaries."""

    payload = historicjoa_response_payload["data"][0]

    item = HistoricJoaEndpoint.Item.model_validate(payload)

    assert item.usajobs_control_number == 123456789
    assert item.hiring_agency_code == "NASA"
    assert item.hiring_agency_name == "National Aeronautics and Space Administration"
    assert item.hiring_department_code == "NAT"
    assert item.hiring_department_name == "Department of Science"
    assert item.agency_level == 2
    assert item.appointment_type == "Permanent"
    assert item.position_title == "Data Scientist"
    assert item.position_open_date == dt.date(2020, 1, 1)
    assert item.position_close_date == dt.date(2020, 2, 1)
    assert item.minimum_salary == 90000.0
    assert item.maximum_salary == 120000.0
    assert item.telework_eligible is True
    assert item.security_clearance_required is True
    assert item.security_clearance == "Secret"
    assert item.supervisory_status is False
    assert item.drug_test_required is False
    assert item.relocation_expenses_reimbursed is True
    assert item.disable_apply_online is False
    assert len(item.hiring_paths) == 1
    assert item.hiring_paths[0].hiring_path == "The public"
    assert len(item.job_categories) == 1
    assert item.job_categories[0].series == "1550"
    assert len(item.position_locations) == 1
    location = item.position_locations[0]
    assert location.position_location_city == "Houston"
    assert location.position_location_state == "Texas"
    assert location.position_location_country == "United States"


def test_response_next_token_returns_continuation(historicjoa_response_payload) -> None:
    """Check Response.next_token surfaces continuation tokens from paging metadata."""

    response = HistoricJoaEndpoint.Response.model_validate(historicjoa_response_payload)

    assert response.next_token() == "NEXTTOKEN"


def test_response_next_token_when_paging_missing() -> None:
    """Validate Response.next_token returns None when paging metadata is absent."""

    response = HistoricJoaEndpoint.Response(data=[])

    assert response.next_token() is None
