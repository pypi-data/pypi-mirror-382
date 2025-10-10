"""
Wrapper for the Historic JOAs API.

Access archived job opportunity announcements with date filters, control numbers, and hiring-organization metadata.

- Feed a control number captured from a [search result item's `id`][usajobsapi.endpoints.search.SearchEndpoint.JOAItem] into [`usajobs_control_numbers`][usajobsapi.endpoints.historicjoa.HistoricJoaEndpoint.Params] to retrieve historical records for the same posting.
- Date filters such as [`start_position_open_date`][usajobsapi.endpoints.historicjoa.HistoricJoaEndpoint.Params] normalize strings as `datetime.date` objects and are reflected back in a response's `position_open_date`.
- Boolean indicators rely on normalization validators to handle the API's inconsistent input/output formats for booleans.
"""

import datetime as dt
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from usajobsapi.utils import _dump_by_alias, _normalize_date, _normalize_yn_bool


class HistoricJoaEndpoint(BaseModel):
    """
    Declarative wrapper around the [Historic JOAs API](https://developer.usajobs.gov/api-reference/get-api-historicjoa).
    """

    METHOD: str = "GET"
    PATH: str = "/api/historicjoa"

    class Params(BaseModel):
        """Declarative definition of the endpoint's query parameters."""

        model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

        hiring_agency_codes: Optional[str] = Field(
            None, serialization_alias="HiringAgencyCodes"
        )
        hiring_department_codes: Optional[str] = Field(
            None, serialization_alias="HiringDepartmentCodes"
        )
        position_series: Optional[str] = Field(
            None, serialization_alias="PositionSeries"
        )
        announcement_numbers: Optional[str] = Field(
            None, serialization_alias="AnnouncementNumbers"
        )
        usajobs_control_numbers: Optional[str] = Field(
            None, serialization_alias="USAJOBSControlNumbers"
        )
        start_position_open_date: Optional[dt.date] = Field(
            default=None, serialization_alias="StartPositionOpenDate"
        )
        end_position_open_date: Optional[dt.date] = Field(
            default=None, serialization_alias="EndPositionOpenDate"
        )
        start_position_close_date: Optional[dt.date] = Field(
            default=None, serialization_alias="StartPositionCloseDate"
        )
        end_position_close_date: Optional[dt.date] = Field(
            default=None, serialization_alias="EndPositionCloseDate"
        )
        continuation_token: Optional[str] = Field(
            None, serialization_alias="continuationToken"
        )

        def to_params(self) -> Dict[str, str]:
            """Serialize params into payload-ready query parameters."""
            return _dump_by_alias(self)

        @field_validator(
            "start_position_open_date",
            "end_position_open_date",
            "start_position_close_date",
            "end_position_close_date",
            mode="before",
        )
        @classmethod
        def _normalize_date_fields(
            cls, value: None | dt.datetime | dt.date | str
        ) -> Optional[dt.date]:
            """Coerce date-like inputs to `datetime.date`."""

            return _normalize_date(value)

    # Response shapes
    # ---

    class Item(BaseModel):
        """A single historic job opportunity announcement record."""

        class HiringPath(BaseModel):
            hiring_path: Optional[str] = Field(default=None, alias="hiringPath")

        class JobCategory(BaseModel):
            series: Optional[str] = Field(default=None, alias="series")

        class PositionLocation(BaseModel):
            position_location_city: Optional[str] = Field(
                default=None, alias="positionLocationCity"
            )
            position_location_state: Optional[str] = Field(
                default=None, alias="positionLocationState"
            )
            position_location_country: Optional[str] = Field(
                default=None, alias="positionLocationCountry"
            )

        usajobs_control_number: int = Field(alias="usajobsControlNumber")
        hiring_agency_code: Optional[str] = Field(
            default=None, alias="hiringAgencyCode"
        )
        hiring_agency_name: Optional[str] = Field(
            default=None, alias="hiringAgencyName"
        )
        hiring_department_code: Optional[str] = Field(
            default=None, alias="hiringDepartmentCode"
        )
        hiring_department_name: Optional[str] = Field(
            default=None, alias="hiringDepartmentName"
        )
        agency_level: Optional[int] = Field(default=None, alias="agencyLevel")
        agency_level_sort: Optional[str] = Field(default=None, alias="agencyLevelSort")
        appointment_type: Optional[str] = Field(default=None, alias="appointmentType")
        work_schedule: Optional[str] = Field(default=None, alias="workSchedule")
        pay_scale: Optional[str] = Field(default=None, alias="payScale")
        salary_type: Optional[str] = Field(default=None, alias="salaryType")
        vendor: Optional[str] = Field(default=None, alias="vendor")
        travel_requirement: Optional[str] = Field(
            default=None, alias="travelRequirement"
        )
        telework_eligible: Optional[bool] = Field(
            default=None, alias="teleworkEligible"
        )
        service_type: Optional[str] = Field(default=None, alias="serviceType")
        security_clearance_required: Optional[bool] = Field(
            default=None, alias="securityClearanceRequired"
        )
        security_clearance: Optional[str] = Field(
            default=None, alias="securityClearance"
        )
        who_may_apply: Optional[str] = Field(default=None, alias="whoMayApply")
        announcement_closing_type_code: Optional[str] = Field(
            default=None, alias="announcementClosingTypeCode"
        )
        announcement_closing_type_description: Optional[str] = Field(
            default=None, alias="announcementClosingTypeDescription"
        )
        position_open_date: Optional[dt.date] = Field(
            default=None, alias="positionOpenDate"
        )
        position_close_date: Optional[dt.date] = Field(
            default=None, alias="positionCloseDate"
        )
        position_expire_date: Optional[dt.date] = Field(
            default=None, alias="positionExpireDate"
        )
        announcement_number: Optional[str] = Field(
            default=None, alias="announcementNumber"
        )
        hiring_subelement_name: Optional[str] = Field(
            default=None, alias="hiringSubelementName"
        )
        position_title: Optional[str] = Field(default=None, alias="positionTitle")
        minimum_grade: Optional[str] = Field(default=None, alias="minimumGrade")
        maximum_grade: Optional[str] = Field(default=None, alias="maximumGrade")
        promotion_potential: Optional[str] = Field(
            default=None, alias="promotionPotential"
        )
        minimum_salary: Optional[float] = Field(default=None, alias="minimumSalary")
        maximum_salary: Optional[float] = Field(default=None, alias="maximumSalary")
        supervisory_status: Optional[bool] = Field(
            default=None, alias="supervisoryStatus"
        )
        drug_test_required: Optional[bool] = Field(
            default=None, alias="drugTestRequired"
        )
        relocation_expenses_reimbursed: Optional[bool] = Field(
            default=None, alias="relocationExpensesReimbursed"
        )
        total_openings: Optional[str] = Field(default=None, alias="totalOpenings")
        disable_apply_online: Optional[bool] = Field(
            default=None, alias="disableApplyOnline"
        )
        position_opening_status: Optional[str] = Field(
            default=None, alias="positionOpeningStatus"
        )
        hiring_paths: List["HistoricJoaEndpoint.Item.HiringPath"] = Field(
            default_factory=list, alias="hiringPaths"
        )
        job_categories: List["HistoricJoaEndpoint.Item.JobCategory"] = Field(
            default_factory=list, alias="jobCategories"
        )
        position_locations: List["HistoricJoaEndpoint.Item.PositionLocation"] = Field(
            default_factory=list, alias="positionLocations"
        )

        @field_validator(
            "telework_eligible",
            "security_clearance_required",
            "supervisory_status",
            "drug_test_required",
            "relocation_expenses_reimbursed",
            "disable_apply_online",
            mode="before",
        )
        @classmethod
        def _normalize_yn_boolean(cls, value: None | bool | str) -> Optional[bool]:
            """Coerce bool-like outputs to `bool`."""

            return _normalize_yn_bool(value)

    class PagingMeta(BaseModel):
        """Pagination metadata returned alongside Historic JOA results."""

        total_count: Optional[int] = Field(default=None, alias="totalCount")
        page_size: Optional[int] = Field(default=None, alias="pageSize")
        continuation_token: Optional[str] = Field(
            default=None, alias="continuationToken"
        )

    class Paging(BaseModel):
        """Container for pagination metadata and optional navigation links."""

        metadata: "HistoricJoaEndpoint.PagingMeta"
        next: Optional[str] = None

    class Response(BaseModel):
        """Declarative definition of the endpoint's response object."""

        paging: Optional["HistoricJoaEndpoint.Paging"] = None
        data: List["HistoricJoaEndpoint.Item"] = Field(default_factory=list)

        def next_token(self) -> Optional[str]:
            """Return the continuation token for requesting the next page."""

            return (
                self.paging.metadata.continuation_token
                if self.paging and self.paging.metadata
                else None
            )
