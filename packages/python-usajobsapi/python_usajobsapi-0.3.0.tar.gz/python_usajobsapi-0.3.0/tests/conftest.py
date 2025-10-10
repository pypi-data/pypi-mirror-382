from collections.abc import Callable, Sequence
from copy import deepcopy
from typing import Any

import pytest

from usajobsapi.endpoints.search import HiringPath

_DEFAULT_SEARCH_RESULT_ITEM: dict[str, Any] = {
    "MatchedObjectId": 1,
    "MatchedObjectDescriptor": {
        "PositionID": "24-123456",
        "PositionTitle": "Engineer",
        "PositionURI": "https://example.com/job/1",
        "ApplyURI": ["https://example.com/apply/1"],
        "OrganizationName": "NASA",
        "DepartmentName": "National Aeronautics and Space Administration",
        "PositionLocationDisplay": "Houston, TX",
        "PositionLocation": [
            {
                "LocationName": "Houston, Texas",
                "LocationCode": "TX1234",
                "CountryCode": "US",
                "CountrySubDivisionCode": "TX",
                "CityName": "Houston",
                "Latitude": "29.7604",
                "Longitude": "-95.3698",
            }
        ],
        "JobCategory": [{"Code": "0801", "Name": "General Engineering"}],
        "JobGrade": [{"Code": "GS", "CurrentGrade": "12"}],
        "PositionSchedule": [{"Code": "1", "Name": "Full-time"}],
        "PositionOfferingType": [{"Code": "15317", "Name": "Permanent"}],
        "MinimumRange": 50000.0,
        "MaximumRange": 100000.0,
        "PositionRemuneration": [
            {
                "MinimumRange": "50000",
                "MaximumRange": "100000",
                "RateIntervalCode": "PA",
                "Description": "Per Year",
            }
        ],
        "ApplicationCloseDate": "2024-01-01",
        "UserArea": {
            "Details": {
                "JobSummary": "Design and build spacecraft components.",
                "WhoMayApply": {
                    "Name": "Open to the public",
                    "Code": "public",
                },
            }
        },
    },
}

_DEFAULT_HISTORICJOA_ITEMS: list[dict[str, Any]] = [
    {
        "usajobsControlNumber": 123456789,
        "hiringAgencyCode": "NASA",
        "hiringAgencyName": "National Aeronautics and Space Administration",
        "hiringDepartmentCode": "NAT",
        "hiringDepartmentName": "Department of Science",
        "agencyLevel": 2,
        "agencyLevelSort": "Department of Science\\NASA",
        "appointmentType": "Permanent",
        "workSchedule": "Full-time",
        "payScale": "GS",
        "salaryType": "Per Year",
        "vendor": "USASTAFFING",
        "travelRequirement": "Occasional travel",
        "teleworkEligible": "Y",
        "serviceType": "Competitive",
        "securityClearanceRequired": "Y",
        "securityClearance": "Secret",
        "whoMayApply": "United States Citizens",
        "announcementClosingTypeCode": "C",
        "announcementClosingTypeDescription": "Closing Date",
        "positionOpenDate": "2020-01-01",
        "positionCloseDate": "2020-02-01",
        "positionExpireDate": None,
        "announcementNumber": "NASA-20-001",
        "hiringSubelementName": "Space Operations",
        "positionTitle": "Data Scientist",
        "minimumGrade": "12",
        "maximumGrade": "13",
        "promotionPotential": "13",
        "minimumSalary": 90000.0,
        "maximumSalary": 120000.0,
        "supervisoryStatus": "N",
        "drugTestRequired": "N",
        "relocationExpensesReimbursed": "Y",
        "totalOpenings": "3",
        "disableApplyOnline": "N",
        "positionOpeningStatus": "Accepting Applications",
        "hiringPaths": [{"hiringPath": "The public"}],
        "jobCategories": [{"series": "1550"}],
        "positionLocations": [
            {
                "positionLocationCity": "Houston",
                "positionLocationState": "Texas",
                "positionLocationCountry": "United States",
            }
        ],
    },
    {
        "usajobsControlNumber": 987654321,
        "hiringAgencyCode": "DOE",
        "hiringAgencyName": "Department of Energy",
        "hiringDepartmentCode": "ENG",
        "hiringDepartmentName": "Department of Energy",
        "agencyLevel": 1,
        "agencyLevelSort": "Department of Energy",
        "appointmentType": "Term",
        "workSchedule": "Part-time",
        "payScale": "GS",
        "salaryType": "Per Year",
        "vendor": "OTHER",
        "travelRequirement": "Not required",
        "teleworkEligible": "N",
        "serviceType": None,
        "securityClearanceRequired": "N",
        "securityClearance": "Not Required",
        "whoMayApply": "Agency Employees Only",
        "announcementClosingTypeCode": None,
        "announcementClosingTypeDescription": None,
        "positionOpenDate": "2020-03-01",
        "positionCloseDate": "2020-04-01",
        "positionExpireDate": "2020-04-15",
        "announcementNumber": "DOE-20-ENG",
        "hiringSubelementName": "Energy Research",
        "positionTitle": "Backend Engineer",
        "minimumGrade": "11",
        "maximumGrade": "12",
        "promotionPotential": None,
        "minimumSalary": 80000.0,
        "maximumSalary": 110000.0,
        "supervisoryStatus": "Y",
        "drugTestRequired": "Y",
        "relocationExpensesReimbursed": "N",
        "totalOpenings": "1",
        "disableApplyOnline": "Y",
        "positionOpeningStatus": "Closed",
        "hiringPaths": [{"hiringPath": "Government employees"}],
        "jobCategories": [{"series": "2210"}],
        "positionLocations": [
            {
                "positionLocationCity": "Washington",
                "positionLocationState": "District of Columbia",
                "positionLocationCountry": "United States",
            }
        ],
    },
]


@pytest.fixture
def search_params_kwargs() -> dict[str, Any]:
    """Field-value mapping used to build ``SearchEndpoint.Params`` models."""

    return {
        "keyword": "developer",
        "location_names": ["City, ST", "Town, ST2"],
        "radius": 25,
        "relocation": True,
        "job_category_codes": ["001", "002"],
        "hiring_paths": [HiringPath.PUBLIC, HiringPath.VET],
    }


@pytest.fixture
def make_search_result_item() -> Callable[..., dict[str, Any]]:
    """Return a factory that produces search result item payloads."""

    def _make(
        *,
        matched_object_id: int = 1,
        descriptor_overrides: dict[str, Any] | None = None,
        **overrides: Any,
    ) -> dict[str, Any]:
        item = deepcopy(_DEFAULT_SEARCH_RESULT_ITEM)
        item["MatchedObjectId"] = matched_object_id
        descriptor = item["MatchedObjectDescriptor"]
        if descriptor_overrides:
            descriptor.update(descriptor_overrides)
        if overrides:
            item.update(overrides)
        return item

    return _make


@pytest.fixture
def search_result_item(
    make_search_result_item: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    """Default sample search result item used across unit tests."""

    return make_search_result_item()


@pytest.fixture
def make_search_result_payload(
    make_search_result_item: Callable[..., dict[str, Any]],
) -> Callable[..., dict[str, Any]]:
    """Return a factory that produces serialized search result payloads."""

    def _make(
        *,
        items: Sequence[dict[str, Any]] | None = None,
        count: int | None = None,
        total: int | None = None,
        include_total: bool = True,
    ) -> dict[str, Any]:
        payload_items = (
            [deepcopy(item) for item in items]
            if items is not None
            else [
                make_search_result_item(matched_object_id=1),
                make_search_result_item(
                    matched_object_id=2,
                    descriptor_overrides={"PositionTitle": "Analyst"},
                ),
                make_search_result_item(
                    matched_object_id=3,
                    descriptor_overrides={"PositionID": "3"},
                ),
            ]
        )
        result_count = count if count is not None else len(payload_items)
        payload: dict[str, Any] = {
            "SearchResultCount": result_count,
            "SearchResultItems": payload_items,
        }
        if include_total:
            total_count = total if total is not None else result_count
            payload["SearchResultCountAll"] = total_count
        return payload

    return _make


@pytest.fixture
def search_result_payload(
    make_search_result_payload: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    """Serialized payload matching the API's job summary schema."""

    return make_search_result_payload()


@pytest.fixture
def make_search_response_payload(
    make_search_result_payload: Callable[..., dict[str, Any]],
) -> Callable[..., dict[str, Any]]:
    """Return a factory that produces serialized search endpoint responses."""

    def _make(
        *,
        items: Sequence[dict[str, Any]] | None = None,
        count: int | None = None,
        total: int | None = None,
        include_total: bool = True,
        language: str = "EN",
        keyword: str | None = "python",
        location_names: Sequence[str] | None = ("Atlanta,%20Georgia",),
        page: int | None = None,
        results_per_page: int | None = None,
        extra_params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        search_params: dict[str, Any] = {}
        if keyword is not None:
            search_params["Keyword"] = keyword
        if location_names:
            search_params["LocationName"] = list(location_names)
        if page is not None:
            search_params["Page"] = page
        if results_per_page is not None:
            search_params["ResultsPerPage"] = results_per_page
        if extra_params:
            search_params.update(extra_params)

        return {
            "LanguageCode": language,
            "SearchParameters": search_params,
            "SearchResult": make_search_result_payload(
                items=items,
                count=count,
                total=total,
                include_total=include_total,
            ),
        }

    return _make


@pytest.fixture
def search_response_payload(
    make_search_response_payload: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    """Serialized search endpoint response payload."""

    return make_search_response_payload()


@pytest.fixture
def historicjoa_params_kwargs() -> dict[str, str]:
    """Field-value mapping used to build ``HistoricJoaEndpoint.Params`` models."""

    return {
        "hiring_agency_codes": "AGENCY1",
        "hiring_department_codes": "DEPT1",
        "position_series": "2210",
        "announcement_numbers": "23-ABC",
        "usajobs_control_numbers": "1234567",
        "start_position_open_date": "2020-01-01",
        "end_position_open_date": "2020-12-31",
        "start_position_close_date": "2021-01-01",
        "end_position_close_date": "2021-12-31",
        "continuation_token": "token123",
    }


@pytest.fixture
def make_historicjoa_item() -> Callable[..., dict[str, Any]]:
    """Return a factory that produces historic JOA item payloads."""

    def _make(*, base: int = 0, **overrides: Any) -> dict[str, Any]:
        item = deepcopy(_DEFAULT_HISTORICJOA_ITEMS[base])
        if overrides:
            item.update(overrides)
        return item

    return _make


@pytest.fixture
def make_historicjoa_response_payload(
    make_historicjoa_item: Callable[..., dict[str, Any]],
) -> Callable[..., dict[str, Any]]:
    """Return a factory that produces historic JOA endpoint responses."""

    def _make(
        *,
        items: Sequence[dict[str, Any]] | None = None,
        continuation_token: str | None = "NEXTTOKEN",
        total_count: int = 2,
        page_size: int = 2,
        next_url: str | None = "https://example.invalid/historicjoa?page=2",
    ) -> dict[str, Any]:
        payload_items = (
            [deepcopy(item) for item in items]
            if items is not None
            else [
                make_historicjoa_item(base=0),
                make_historicjoa_item(base=1),
            ]
        )
        metadata = {
            "totalCount": total_count,
            "pageSize": page_size,
            "continuationToken": continuation_token,
        }
        return {
            "paging": {"metadata": metadata, "next": next_url},
            "data": payload_items,
        }

    return _make


@pytest.fixture
def historicjoa_response_payload(
    make_historicjoa_response_payload: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    """Serialized historic JOA response payload mimicking the USAJOBS API."""

    return make_historicjoa_response_payload()
