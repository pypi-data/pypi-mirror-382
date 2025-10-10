"""
Wrapper for the Job Search API.

The search endpoint wraps the core USAJOBS Job Search API. Enumerations describe allowed
query values, the nested [`Params`][usajobsapi.endpoints.search.SearchEndpoint.Params] model validates input, and the response graph mirrors
the payload returned from the API.

- Filter inputs such as [`hiring_path`][usajobsapi.endpoints.search.SearchEndpoint.Params] and [`pay_grade_high`][usajobsapi.endpoints.search.SearchEndpoint.Params] are surfaced in a [search result's `params` field][usajobsapi.endpoints.search.SearchEndpoint.Response] so you can inspect what was sent to USAJOBS.
- Each [`JOAItem`][usajobsapi.endpoints.search.SearchEndpoint.JOAItem] contains a [`JOADescriptor`][usajobsapi.endpoints.search.SearchEndpoint.JOADescriptor] with rich metadata (for example, [`PositionRemuneration`][usajobsapi.endpoints.search.SearchEndpoint.PositionRemuneration]) that aligns with the salary filter parameters.
- [`SearchEndpoint.Response.jobs`][usajobsapi.endpoints.search.SearchEndpoint.Response.jobs] returns the flattened list of [`JOAItem`][usajobsapi.endpoints.search.SearchEndpoint.JOAItem] instances that correspond to the [`items`][usajobsapi.endpoints.search.SearchEndpoint.SearchResult] in the response payload.
"""

from __future__ import annotations

import datetime as dt
from enum import StrEnum
from typing import Annotated, Any, Dict, List, Optional

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    ValidationInfo,
    field_validator,
    model_validator,
)

from usajobsapi.endpoints._validators import isvalid_pay_grade
from usajobsapi.utils import _dump_by_alias, _normalize_date

# Enums for query-params
# ---


class SortField(StrEnum):
    """Sort the search by the specified field."""

    OPEN_DATE = "opendate"
    CLOSED_DATE = "closedate"
    ORGANIZATION_NAME = "organizationname"
    JOB_TITLE = "jobtitle"
    POSITION_TITLE = "positiontitle"
    OPENING_DATE = "openingdate"
    CLOSING_DATE = "closingdate"
    HO_NAME = "honame"
    SALARY_MIN = "salarymin"
    LOCATION = "location"
    DEPARTMENT = "department"
    TITLE = "title"
    AGENCY = "agency"
    SALARY = "salary"


class SortDirection(StrEnum):
    """Sort the search by the SortField specified, in the direction specified."""

    ASC = "Asc"
    DESC = "Desc"


class WhoMayApply(StrEnum):
    """Filter the search by the specified candidate designation."""

    ALL = "All"
    PUBLIC = "Public"
    STATUS = "Status"


class FieldsMinMax(StrEnum):
    """Return the minimum or maximum number of fields for each result item."""

    MIN = "Min"  # Return only the job summary
    FULL = "Full"


class HiringPath(StrEnum):
    """Filter search results by the specified hiring path(s)."""

    PUBLIC = "public"
    VET = "vet"
    N_GUARD = "nguard"
    DISABILITY = "disability"
    NATIVE = "native"
    M_SPOUSE = "mspouse"
    STUDENT = "student"
    SES = "ses"
    PEACE = "peace"
    OVERSEAS = "overseas"
    FED_INTERNAL_SEARCH = "fed-internal-search"
    GRADUATES = "graduates"
    FED_EXCEPTED = "fed-excepted"
    FED_COMPETITIVE = "fed-competitive"
    FED_TRANSITION = "fed-transition"
    LAND = "land"
    SPECIAL_AUTHORITIES = "special-authorities"


# Endpoint declaration
# ---
class SearchEndpoint(BaseModel):
    """
    Declarative wrapper around the [Job Search API](https://developer.usajobs.gov/api-reference/get-api-search).
    """

    METHOD: str = "GET"
    PATH: str = "/api/search"

    class Params(BaseModel):
        """Declarative definition of the endpoint's query parameters."""

        model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

        keyword: Optional[str] = Field(
            None,
            alias="Keyword",
            description="Issues search to find hits based on a keyword. Optional. Keyword will search for all of the words specified (or synonyms of the word) throughout the job announcement.",
            examples=["https://data.usajobs.gov/api/search?Keyword=Software"],
        )
        position_title: Optional[str] = Field(
            None,
            alias="PositionTitle",
            description="""
            Issues search to find hits in the title of the job.

            This is the job title - e.g. IT Specialist, Psychologist, etc. The title search will be treated as 'contains' and will select all job announcements where the job title contains the value provided.""",
            examples=[
                "The following query will return all job announcements with 'psychologist' or a synonym of psychologist in the title: 'https://data.usajobs.gov/api/Search?PositionTitle=Psychologist'",
                "The following query will return all job announcements with 'Electrical Engineer'' in the title: 'https://data.usajobs.gov/api/Search?PositionTitle=Electrical%20Engineer'",
            ],
        )

        remuneration_min: Optional[int] = Field(
            None,
            alias="RemunerationMinimumAmount",
            description="""
            Issues search to find hits with the minimum salary specified.

            Jobs are placed in salary buckets: $0-$24,999, $25,000-$49,999, $50,000-$74,999, $75,000-$99,999, $100,000-$124,999, $125,000-$149,999, $150,000-$174,999, $175,000-$199,999 and $200,000 or greater. So a search with a minimum salary of $15,500 will return jobs with a minimum salary in the $0-$24,999 range.""",
            examples=[
                "https://data.usajobs.gov/api/Search?RemunerationMinimumAmount=15000"
            ],
            ge=0,
        )
        remuneration_max: Optional[int] = Field(
            None,
            alias="RemunerationMaximumAmount",
            description="""
            Issues search to find hits with the maximum salary specified.

            Jobs are placed in salary buckets: $0-$24,999, $25,000-$49,999, $50,000-$74,999, $75,000-$99,999, $100,000-$124,999, $125,000-$149,999, $150,000-$174,999, $175,000-$199,999 and $200,000 or greater. So a search with a maximum salary of $72,000 will return jobs with a maximum salary in the $50,000-$74,999 range.
            """,
            examples=[
                "https://data.usajobs.gov/api/Search?RemunerationMinimumAmount=26000&RemunerationMaximumAmount=85000"
            ],
            gt=0,
        )

        pay_grade_high: Annotated[Optional[str], AfterValidator(isvalid_pay_grade)] = (
            Field(
                None,
                alias="PayGradeHigh",
                description="""
                Issues search to find hits with the maximum pay grade specified. Must be 01 through 15. This is the ending grade for the job. (Caution: Fed speak ahead but it cannot be helped.) The grade along with series is used by the Federal government to categorize and define jobs.

                For more information on what series and grade are, please visit: https://help.usajobs.gov/index.php/What_is_a_series_and_or_grade%3F.

                However, grade is also used to define salary. USAJOBS search uses grades for the General Schedule (GS) pay plan ( http://www.opm.gov/policy-data-oversight/pay-leave/salaries-wages).

                For jobs that use a different pay plan than the GS schedule, USAJOBS will derive the corresponding grade by using the minimum and maximum salary and the wages for the GS schedule for the Rest of the United States (for 2014, see: http//www.opm.gov/policy-data-oversight/pay-leave/salaries-wages/salary-tables/14Tables/html/RUS.aspx).

                For federal employees, especially those who have a GS pay plan, searching by grade is extremely useful since they would already know which grades they are or qualify for. However, for non-GS employees, searching by salary is much simpler.
                """,
                examples=["https://data.usajobs.gov/api/Search?PayGradeHigh=07"],
            )
        )
        pay_grade_low: Annotated[Optional[str], AfterValidator(isvalid_pay_grade)] = (
            Field(
                None,
                alias="PayGradeLow",
                description="Issues search to find hits with the minimum pay grade specified. Must be 01 through 15. This is the beginning grade for the job. See PayGradeHigh for more information.",
                examples=[
                    "https://data.usajobs.gov/api/Search?PayGradeLow=04",
                    "https://data.usajobs.gov/api/Search?PayGradeLow=07&PayGradeHigh=09",
                ],
            )
        )

        job_category_codes: List[str] = Field(
            default_factory=list,
            alias="JobCategoryCode",
            description="Issues a search to find hits with the job category series specified.",
            examples=["https://data.usajobs.gov/api/Search?JobCategoryCode=0830"],
        )
        position_schedule_type_codes: List[int] = Field(
            default_factory=list,
            alias="PositionScheduleTypeCode",
            description="Issues a search to find hits for jobs matching the specified job schedule. This field is also known as work schedule.",
            examples=["https://data.usajobs.gov/api/Search?PositionSchedule=4"],
        )
        position_offering_type_codes: List[int] = Field(
            default_factory=list,
            alias="PositionOfferingTypeCode",
            description="Issues a search to find jobs within the specified type. This field is also known as Work Type.",
        )

        organization: List[str] = Field(
            default_factory=list,
            alias="Organization",
            description="Issues a search to find jobs for the specified agency using the Agency Subelement Code.",
            examples=["https://data.usajobs.gov/api/Search?Organization=TR"],
        )

        location_names: List[str] = Field(
            default_factory=list,
            alias="LocationName",
            description="Issues a search to find hits within the specified location. This is the city or military installation name. LocationName simplifies location based search as the user does not need to know or account for each and every Location Code. LocationName will search for all location codes and ZIP codes that have that specific description.",
            examples=[
                "https://data.usajobs.gov/api/Search?LocationName=Washington%20DC,%20District%20of%20Columbia",
                "https://data.usajobs.gov/api/Search?LocationName=Atlanta,%20Georgia",
            ],
        )

        travel_percentage: List[int] = Field(
            default_factory=list,
            alias="TravelPercentage",
            description="Issues a search to find hits for jobs matching the specified travel level.",
            examples=[
                "https://data.usajobs.gov/api/Search?TravelPercentage=0",
                "https://data.usajobs.gov/api/Search?TravelPercentage=7",
            ],
            ge=0,
            le=8,
        )
        relocation: Optional[bool] = Field(
            None,
            alias="RelocationIndicator",
            description="Issues a search to find hits for jobs matching the relocation filter.",
        )
        security_clearance_required: List[int] = Field(
            default_factory=list,
            alias="SecurityClearanceRequired",
            description="Issues a search to find hits for jobs matching the specified security clearance.",
            examples=[
                "https://data.usajobs.gov/api/Search?SecurityClearanceRequired=1"
            ],
            ge=0,
            le=8,
        )

        supervisory_status: Optional[str] = Field(
            None,
            alias="SupervisoryStatus",
            description="Issues a search to find hits for jobs matching the specified supervisory status.",
        )

        days_since_posted: Annotated[
            Optional[int],
            Field(
                alias="DatePosted",
                description="Issues a search to find hits for jobs that were posted within the number of days specified.",
                strict=True,
                ge=0,
                le=60,
            ),
        ] = None
        job_grade_codes: List[str] = Field(
            default_factory=list,
            alias="JobGradeCode",
            description="Issues a search to find hits for jobs matching the grade code specified. This field is also known as Pay Plan.",
        )

        sort_field: Optional[SortField] = Field(
            None,
            alias="SortField",
            description="Issues a search that will be sorted by the specified field.",
            examples=[
                "https://data.usajobs.gov/api/Search?PositionTitle=Electrical&SortField=PositionTitle"
            ],
        )
        sort_direction: Optional[SortDirection] = Field(
            None,
            alias="SortDirection",
            description="Issues a search that will be sorted by the SortField specified, in the direction specified.",
        )

        page: Annotated[
            Optional[int],
            Field(
                alias="Page",
                description="Issues a search to pull the paged results specified.",
                strict=True,
                ge=1,
            ),
        ] = None
        results_per_page: Annotated[
            Optional[int],
            Field(
                alias="ResultsPerPage",
                description="Issues a search and returns the page size specified. In this example, 25 jobs will be return for the first page.",
                strict=True,
                ge=1,
                le=500,
            ),
        ] = None

        who_may_apply: Optional[WhoMayApply] = Field(
            None,
            alias="WhoMayApply",
            description="Issues a search to find hits based on the desired candidate designation. In this case, public will find jobs that U.S. citizens can apply for.",
            examples=["https://data.usajobs.gov/api/Search?WhoMayApply=public"],
        )

        radius: Annotated[
            Optional[int],
            Field(
                alias="Radius",
                description="Issues a search when used along with LocationName, will expand the locations, based on the radius specified.",
                examples=[
                    "https://data.usajobs.gov/api/Search?LocationName=Norfolk%20Virginia&Radius=75"
                ],
                strict=True,
                gt=0,
            ),
        ] = None
        fields: Optional[FieldsMinMax] = Field(
            None,
            alias="Fields",
            description="Issues a search that will return the minimum fields or maximum number of fields in the job. Min returns only the job summary.",
            examples=[
                "https://data.usajobs.gov/api/Search?TravelPercentage=7&Fields=full",
                "https://data.usajobs.gov/api/Search?SecurityClearanceRequired=1&Fields=full",
            ],
        )

        salary_bucket: List[int] = Field(
            default_factory=list,
            alias="SalaryBucket",
            description="Issues a search that will find hits for salaries matching the grouping specified. Buckets are assigned based on salary ranges.",
        )
        grade_bucket: List[int] = Field(
            default_factory=list,
            alias="GradeBucket",
            description="Issues a search that will find hits for grades that match the grouping specified.",
        )

        hiring_paths: List[HiringPath] = Field(
            default_factory=list,
            alias="HiringPath",
            description="Issues a search that will find hits for hiring paths that match the hiring paths specified.",
            examples=["https://data.usajobs.gov/api/Search?HiringPath=public"],
        )

        mission_critical_tags: List[str] = Field(
            default_factory=list,
            alias="MissionCriticalTags",
            description="Issues a search that will find hits for mission critical tags that match the grouping specified.",
            examples=[
                "https://data.usajobs.gov/api/Search?MissionCriticalTags=STEM&Fields=full"
            ],
        )

        position_sensitivity: List[int] = Field(
            default_factory=list,
            alias="PositionSensitivity",
            description="Issues a search that will find hits for jobs matching the position sensitivity and risk specified.",
            examples=["https://data.usajobs.gov/api/Search?PositionSensitivity=1"],
            ge=1,
            le=7,
        )

        remote_indicator: Optional[bool] = Field(
            None,
            alias="RemoteIndicator",
            description="Issues a search to find hits for jobs matching the remote filter.",
        )

        @model_validator(mode="after")
        def _radius_requires_location(self) -> "SearchEndpoint.Params":
            """Only use radius filters when a locaiton is provided."""
            if self.radius is not None and not self.location_names:
                raise ValueError("Radius requires at least one LocationName.")
            return self

        @field_validator("remuneration_max")
        @classmethod
        def _check_min_le_max(
            cls, v: Optional[int], info: ValidationInfo
        ) -> Optional[int]:
            """Validate that remuneration max is >= remuneration min."""
            mn = info.data.get("remuneration_min")
            if v is not None and mn is not None and v < mn:
                raise ValueError(
                    "RemunerationMaximumAmount must be >= RemunerationMinimumAmount."
                )
            return v

        def to_params(self) -> Dict[str, str]:
            """Return the serialized query-parameter dictionary."""
            return _dump_by_alias(self)

    # Response shapes
    # ---

    class JobCategory(BaseModel):
        """Represents a job series classification associated with a posting."""

        code: Optional[str] = Field(default=None, alias="Code")
        name: Optional[str] = Field(default=None, alias="Name")

    class JobGrade(BaseModel):
        """Represents the job grade (e.g. GS) tied to the posting."""

        code: Optional[str] = Field(default=None, alias="Code")
        current_grade: Optional[str] = Field(default=None, alias="CurrentGrade")

    class PositionSchedule(BaseModel):
        """Represents the work schedule for the position."""

        code: Optional[str] = Field(default=None, alias="Code")
        name: Optional[str] = Field(default=None, alias="Name")

    class PositionOfferingType(BaseModel):
        """Represents the appointment type (e.g. permanent, term)."""

        code: Optional[str] = Field(default=None, alias="Code")
        name: Optional[str] = Field(default=None, alias="Name")

    class PositionRemuneration(BaseModel):
        """Represents a salary range entry for the position."""

        minimum: Optional[float] = Field(default=None, alias="MinimumRange")
        maximum: Optional[float] = Field(default=None, alias="MaximumRange")
        rate_interval_code: Optional[str] = Field(
            default=None, alias="RateIntervalCode"
        )
        description: Optional[str] = Field(default=None, alias="Description")

        @field_validator("minimum", "maximum", mode="before")
        @classmethod
        def _normalize_amount(cls, value: Any) -> Optional[float]:
            """Normalize remuneration amounts to floats."""

            if value in (None, ""):
                return None
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                cleaned = value.replace(",", "").replace("$", "").strip()
                if not cleaned:
                    return None
                try:
                    return float(cleaned)
                except ValueError:
                    return None
            return None

    class JobLocation(BaseModel):
        """Represents a structured job location entry."""

        name: Optional[str] = Field(default=None, alias="LocationName")
        code: Optional[str] = Field(default=None, alias="LocationCode")
        country_code: Optional[str] = Field(default=None, alias="CountryCode")
        state_code: Optional[str] = Field(default=None, alias="CountrySubDivisionCode")
        city_name: Optional[str] = Field(default=None, alias="CityName")
        latitude: Optional[float] = Field(default=None, alias="Latitude")
        longitude: Optional[float] = Field(default=None, alias="Longitude")

        @field_validator("latitude", "longitude", mode="before")
        @classmethod
        def _normalize_coordinate(cls, value: Any) -> Optional[float]:
            """Normalize coordinate values to floats."""

            if value in (None, ""):
                return None
            try:
                return float(value)
            except (TypeError, ValueError):
                return None

    class WhoMayApplyInfo(BaseModel):
        """Represents the structured WhoMayApply block."""

        name: Optional[str] = Field(default=None, alias="Name")
        code: Optional[str] = Field(default=None, alias="Code")

    class PositionFormatDesc(BaseModel):
        """Represents a quick summary of the job opportunity announcement."""

        content: Optional[str] = Field(default=None, alias="Content")
        label: Optional[str] = Field(default=None, alias="Label")
        label_desc: Optional[str] = Field(default=None, alias="LabelDescription")

    class UserAreaDetails(BaseModel):
        """Represents metadata stored under the UserArea.Details field."""

        duties: Optional[str] = Field(
            default=None,
            alias="MajorDuties",
            description="Description of the duties of the job.",
        )
        education: Optional[str] = Field(
            default=None,
            alias="Education",
            description="Education required or preferred by applicants.",
        )
        requirements: Optional[str] = Field(
            default=None,
            alias="Requirements",
            description="Key Requirements of the job opportunity.",
        )
        evaluations: Optional[str] = Field(
            default=None,
            alias="Evaluations",
            description="Qualification requirements of the job opportunity.",
        )
        how_apply: Optional[str] = Field(
            default=None,
            alias="HowToApply",
            description="Description of the steps to take to apply for the job opportunity.",
        )
        what_next: Optional[str] = Field(
            default=None,
            alias="WhatToExpectNext",
            description="Description of what can be expected during the application process.",
        )
        req_docs: Optional[str] = Field(
            default=None,
            alias="RequiredDocuments",
            description="Required documents when applying for the job opportunity.",
        )
        benefits: Optional[str] = Field(
            default=None,
            alias="Benefits being offered as part of the job opportunity.",
            description="BenefitsBenefits",
        )
        benefits_url: Optional[str] = Field(
            default=None,
            alias="BenefitsUrl",
            description="URL to view benefit details being offered.",
        )
        other_info: Optional[str] = Field(
            default=None,
            alias="OtherInformation",
            description="Additional information about the job opportunity.",
        )
        key_reqs: List[str] = Field(
            default_factory=list,
            alias="KeyRequirements",
            description="List of requirements for the job opportunity.",
        )
        job_summary: Optional[str] = Field(
            default=None,
            alias="JobSummary",
            description="Summary of the job opportunity.",
        )

        who_may_apply: Optional[SearchEndpoint.WhoMayApplyInfo] = Field(
            default=None,
            alias="WhoMayApply",
            description="Object that contains values for name and code of who may apply to the job opportunity.",
        )

        low_grade: Optional[str] = Field(
            default=None,
            alias="LowGrade",
            description="Lowest potential grade level for the job opportunity.",
        )
        high_grade: Optional[str] = Field(
            default=None,
            alias="HighGrade",
            description="Highest potential grade level for the job opportunity.",
        )

        sub_agency: Optional[str] = Field(
            default=None,
            alias="SubAgencyName",
            description="SubAgencyName",
        )
        org_codes: Optional[str] = Field(
            default=None,
            alias="OrganizationCodes",
            description="Organization codes separated by a slash (/).",
        )

    class UserArea(BaseModel):
        """Wrapper for additional USAJOBS metadata."""

        details: Optional[SearchEndpoint.UserAreaDetails] = Field(
            default=None, alias="Details"
        )
        is_radial_search: Optional[bool] = Field(
            default=None,
            alias="IsRadialSearch",
            description="Was a radial search preformed.",
        )

    class JOADescriptor(BaseModel):
        position_id: Optional[str] = Field(
            default=None, alias="PositionID", description="Job Announcement Number"
        )
        position_title: Optional[str] = Field(
            default=None,
            alias="PositionTitle",
            description="Title of the job offering.",
        )
        position_uri: Optional[str] = Field(
            default=None,
            alias="PositionURI",
            description="URI to view the job offering.",
        )
        apply_uri: List[str] = Field(
            default_factory=list,
            alias="ApplyURI",
            description="URI to apply for the job offering.",
        )

        locations_display: Optional[str] = Field(
            default=None, alias="PositionLocationDisplay"
        )
        locations: List[SearchEndpoint.JobLocation] = Field(
            default_factory=list,
            alias="PositionLocation",
            description="Contains values for location name, country, country subdivision, city, latitude and longitude.",
        )

        organization_name: Optional[str] = Field(
            default=None,
            alias="OrganizationName",
            description="Name of the organization or agency offering the position.",
        )
        department_name: Optional[str] = Field(
            default=None,
            alias="DepartmentName",
            description="Name of the department within the organization or agency offering the position.",
        )

        job_categories: List[SearchEndpoint.JobCategory] = Field(
            default_factory=list,
            alias="JobCategory",
            description="List of job category objects that contain values for name and code.",
        )
        job_grades: List[SearchEndpoint.JobGrade] = Field(
            default_factory=list,
            alias="JobGrade",
            description="List of job grade objects that contains an code value. This field is also known as Pay Plan.",
        )
        position_schedules: List[SearchEndpoint.PositionSchedule] = Field(
            default_factory=list,
            alias="PositionSchedule",
            description="List of position schedule objects that contains values for name and code.",
        )
        position_offerings: List[SearchEndpoint.PositionOfferingType] = Field(
            default_factory=list,
            alias="PositionOfferingType",
            description="List of position offering type objects that contains values for name and code. See PositionOfferingType in paramters above for list of code values.",
        )

        qualification_summary: Optional[str] = Field(
            default=None,
            alias="QualificationSummary",
            description="Summary of qualifications for the job offering.",
        )

        position_remuneration: List[SearchEndpoint.PositionRemuneration] = Field(
            default_factory=list,
            alias="PositionRemuneration",
            description="List of position remuneration objects that contains MinimumRange, MaximumRange and RateIntervalCode. Gives the pay range and frequency.",
        )
        position_start_date: Optional[dt.date] = Field(
            default=None,
            alias="PositionStartDate",
            description="The date the job opportunity will be open to applications.",
        )
        position_end_date: Optional[dt.date] = Field(
            default=None,
            alias="PositionEndDate",
            description="Last date the job opportunity will be posted",
        )
        publication_start_date: Optional[dt.date] = Field(
            default=None,
            alias="PublicationStartDate",
            description="Date the job opportunity is posted",
        )
        application_close_date: Optional[dt.date] = Field(
            default=None,
            alias="ApplicationCloseDate",
            description="Last date applications will be accepted for the job opportunity",
        )

        position_format_desc: List[SearchEndpoint.PositionFormatDesc] = Field(
            default_factory=list,
            alias="PositionFormattedDescription",
            description="Provides quick summary of job opportunity.",
        )

        user_area: Optional[SearchEndpoint.UserArea] = Field(
            default=None, alias="UserArea"
        )

        @field_validator(
            "position_start_date",
            "position_end_date",
            "publication_start_date",
            "application_close_date",
            mode="before",
        )
        @classmethod
        def _normalize_date_fields(
            cls, value: None | dt.datetime | dt.date | str
        ) -> Optional[dt.date]:
            """Coerce date-like inputs to `datetime.date`."""

            return _normalize_date(value)

        def summary(self) -> Optional[str]:
            """Helper method returning the most descriptive summary for the job."""

            if self.user_area and self.user_area.details:
                details = self.user_area.details
                if self.user_area.details and details.job_summary:
                    return details.job_summary
            return self.qualification_summary

    class JOAItem(BaseModel):
        """Represents a job opportunity annoucement object search result item."""

        id: int = Field(alias="MatchedObjectId", description="Control Number")
        details: SearchEndpoint.JOADescriptor = Field(alias="MatchedObjectDescriptor")
        rank: Optional[float] = Field(default=None, alias="RelevanceRank")

    class SearchResult(BaseModel):
        """Model of paginated search results."""

        result_count: Optional[int] = Field(
            default=None,
            alias="SearchResultCount",
            description="Number of records returned in response object.",
        )
        result_total: Optional[int] = Field(
            default=None,
            alias="SearchResultCountAll",
            description="Total Number of records that matched search criteria.",
        )
        items: List[SearchEndpoint.JOAItem] = Field(
            default_factory=list,
            alias="SearchResultItems",
            description="Array of job opportunity announcement objects that matched search criteria.",
        )

    class Response(BaseModel):
        """Declarative definition of the endpoint's response object."""

        language: Optional[str] = Field(
            default=None, alias="LanguageCode", description="Response Langauge"
        )
        params: Optional[SearchEndpoint.Params] = Field(
            default=None,
            alias="SearchParameters",
            description="Query parameters used in search request.",
        )

        # Results are wrapped under SearchResult
        search_result: Optional[SearchEndpoint.SearchResult] = Field(
            default=None, alias="SearchResult"
        )

        def jobs(self) -> List[SearchEndpoint.JOAItem]:
            """Helper method to directly expose search result items from the response object."""
            if not self.search_result:
                return []
            return self.search_result.items
