import pytest

from usajobsapi.endpoints.search import SearchEndpoint


class TestSearchEndpointParams:
    def test_to_params_serialization(self, search_params_kwargs):
        """Validate Params.to_params uses USAJOBS aliases and formatting."""

        params = SearchEndpoint.Params(**search_params_kwargs)

        serialized = params.to_params()
        expected = {
            "Keyword": "developer",
            "LocationName": "City, ST;Town, ST2",
            "Radius": "25",
            "RelocationIndicator": "True",
            "JobCategoryCode": "001;002",
            "HiringPath": "public;vet",
        }

        assert serialized == expected

    def test_radius_requires_location(self):
        with pytest.raises(ValueError):
            SearchEndpoint.Params.model_validate({"radius": 10})

    def test_remuneration_max_less_than_min(self):
        with pytest.raises(ValueError):
            SearchEndpoint.Params.model_validate(
                {"remuneration_min": 100, "remuneration_max": 50}
            )


class TestSearchEndpointResponses:
    def test_job_summary_parses_nested_fields(self, search_result_item):
        summary = SearchEndpoint.JOAItem.model_validate(search_result_item)

        assert summary.details.position_id == "24-123456"
        assert summary.details.position_uri == "https://example.com/job/1"
        assert summary.details.apply_uri == ["https://example.com/apply/1"]
        assert (
            summary.details.department_name
            == "National Aeronautics and Space Administration"
        )
        assert summary.details.locations_display == "Houston, TX"

        assert len(summary.details.locations) == 1
        location = summary.details.locations[0]
        assert location.city_name == "Houston"
        assert location.state_code == "TX"
        assert location.latitude == pytest.approx(29.7604)
        assert location.longitude == pytest.approx(-95.3698)

        assert summary.details.job_categories[0].code == "0801"
        assert summary.details.job_grades[0].current_grade == "12"
        assert summary.details.position_schedules[0].name == "Full-time"
        assert summary.details.position_offerings[0].code == "15317"

        assert summary.details.summary() == "Design and build spacecraft components."

        assert summary.details.user_area
        assert summary.details.user_area.details
        assert summary.details.user_area.details.who_may_apply
        assert (
            summary.details.user_area.details.who_may_apply.name == "Open to the public"
        )

    def test_search_result_jobs_parsing(self, search_result_payload):
        search_result = SearchEndpoint.SearchResult.model_validate(
            search_result_payload
        )

        jobs = search_result.items
        assert len(jobs) == 3
        assert jobs[0].id == 1
        assert jobs[1].id == 2
        assert jobs[2].details.position_id == "3"

    def test_response_model_parsing(self, search_response_payload):
        resp = SearchEndpoint.Response.model_validate(search_response_payload)

        assert resp.language == "EN"
        assert resp.params is not None
        assert resp.params.keyword == "python"
        assert resp.search_result is not None
        jobs = resp.search_result.items
        assert jobs[0].id == 1

    def test_response_jobs_helper(self, search_response_payload):
        empty_resp = SearchEndpoint.Response.model_validate({})
        assert empty_resp.jobs() == []

        resp = SearchEndpoint.Response.model_validate(search_response_payload)
        jobs = resp.jobs()
        assert len(jobs) == 3
        assert jobs[0].id == 1
