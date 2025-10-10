"""Unit tests for USAJobsClient."""

import pytest

from usajobsapi.client import USAJobsClient
from usajobsapi.endpoints.historicjoa import HistoricJoaEndpoint
from usajobsapi.endpoints.search import SearchEndpoint

# test search_jobs_pages
# ---


def test_search_jobs_pages_yields_pages(
    monkeypatch: pytest.MonkeyPatch,
    make_search_response_payload,
    make_search_result_item,
) -> None:
    """Ensure search_jobs_pages iterates pages based on total counts."""

    responses = [
        SearchEndpoint.Response.model_validate(
            make_search_response_payload(
                items=[
                    make_search_result_item(matched_object_id=1),
                    make_search_result_item(matched_object_id=2),
                ],
                count=2,
                total=5,
            )
        ),
        SearchEndpoint.Response.model_validate(
            make_search_response_payload(
                items=[
                    make_search_result_item(matched_object_id=3),
                    make_search_result_item(matched_object_id=4),
                ],
                count=2,
                total=5,
            )
        ),
        SearchEndpoint.Response.model_validate(
            make_search_response_payload(
                items=[make_search_result_item(matched_object_id=5)],
                count=1,
                total=5,
            )
        ),
    ]

    captured_kwargs: list[dict[str, object]] = []

    def fake_search(self, **call_kwargs):
        captured_kwargs.append(call_kwargs)
        return responses.pop(0)

    monkeypatch.setattr(USAJobsClient, "search_jobs", fake_search)

    client = USAJobsClient()
    pages = list(client.search_jobs_pages(keyword="engineer", results_per_page=2))

    assert len(pages) == 3
    assert [call["page"] for call in captured_kwargs] == [1, 2, 3]
    assert all(call["results_per_page"] == 2 for call in captured_kwargs)


def test_search_jobs_pages_handles_missing_total(
    monkeypatch: pytest.MonkeyPatch,
    make_search_response_payload,
    make_search_result_item,
) -> None:
    """Continue until a short page is returned when total counts are absent."""

    first_page = SearchEndpoint.Response.model_validate(
        make_search_response_payload(
            items=[
                make_search_result_item(matched_object_id=1),
                make_search_result_item(matched_object_id=2),
            ],
            count=2,
            include_total=False,
        )
    )
    final_page = SearchEndpoint.Response.model_validate(
        make_search_response_payload(
            items=[make_search_result_item(matched_object_id=3)],
            count=1,
        )
    )

    responses = [first_page, final_page]
    captured_kwargs: list[dict[str, object]] = []

    def fake_search(self, **call_kwargs):
        captured_kwargs.append(call_kwargs)
        return responses.pop(0)

    monkeypatch.setattr(USAJobsClient, "search_jobs", fake_search)

    client = USAJobsClient()
    pages = list(client.search_jobs_pages(keyword="space"))

    assert len(pages) == 2
    assert [call["page"] for call in captured_kwargs] == [1, 2]
    assert "results_per_page" not in captured_kwargs[0]
    assert captured_kwargs[1]["results_per_page"] == 2


def test_search_jobs_pages_breaks_on_empty_results(
    monkeypatch: pytest.MonkeyPatch,
    make_search_response_payload,
) -> None:
    """Stop pagination when a page returns no results."""

    empty_page = SearchEndpoint.Response.model_validate(
        make_search_response_payload(items=[], count=0, include_total=False)
    )

    def fake_search(self, **_):
        return empty_page

    monkeypatch.setattr(USAJobsClient, "search_jobs", fake_search)

    client = USAJobsClient()
    pages = list(client.search_jobs_pages(keyword="empty"))

    assert len(pages) == 1


# test search_jobs_items
# ---


def test_search_jobs_items_yields_jobs(
    monkeypatch: pytest.MonkeyPatch,
    make_search_response_payload,
    make_search_result_item,
) -> None:
    """Ensure search_jobs_items yields summaries across pages."""

    client = USAJobsClient()

    payloads = [
        make_search_response_payload(
            items=[
                make_search_result_item(matched_object_id=1),
                make_search_result_item(matched_object_id=2),
            ],
            count=2,
            total=3,
            page=1,
            results_per_page=2,
        ),
        make_search_response_payload(
            items=[make_search_result_item(matched_object_id=3)],
            count=1,
            total=3,
            page=2,
            results_per_page=2,
        ),
    ]

    def fake_search_jobs(self, **_):
        return SearchEndpoint.Response.model_validate(payloads.pop(0))

    monkeypatch.setattr(USAJobsClient, "search_jobs", fake_search_jobs)

    summaries = list(client.search_jobs_items(results_per_page=2))

    assert [summary.id for summary in summaries] == [1, 2, 3]


# test historic_joa_pages
# ---


def test_historic_joa_pages_yields_pages(
    monkeypatch: pytest.MonkeyPatch,
    make_historicjoa_response_payload,
) -> None:
    """Ensure historic_joa_pages yields pages while forwarding continuation tokens."""

    responses = [
        HistoricJoaEndpoint.Response.model_validate(
            make_historicjoa_response_payload()
        ),
        HistoricJoaEndpoint.Response.model_validate(
            make_historicjoa_response_payload(
                continuation_token=None,
                items=[],
                next_url=None,
            )
        ),
    ]
    captured_kwargs: list[dict[str, object]] = []

    def fake_historic_joa(self, **call_kwargs):
        captured_kwargs.append(call_kwargs)
        return responses.pop(0)

    monkeypatch.setattr(USAJobsClient, "historic_joa", fake_historic_joa)

    client = USAJobsClient()

    pages = list(
        client.historic_joa_pages(
            hiring_agency_codes="NASA", continuation_token="INITIALTOKEN"
        )
    )

    assert len(pages) == 2
    assert pages[0].next_token() == "NEXTTOKEN"
    assert pages[1].next_token() is None
    assert captured_kwargs == [
        {"hiring_agency_codes": "NASA", "continuation_token": "INITIALTOKEN"},
        {"hiring_agency_codes": "NASA", "continuation_token": "NEXTTOKEN"},
    ]


def test_historic_joa_pages_duplicate_token(
    monkeypatch: pytest.MonkeyPatch,
    make_historicjoa_response_payload,
) -> None:
    """Duplicate continuation tokens should raise to avoid infinite loops."""

    first_response = HistoricJoaEndpoint.Response.model_validate(
        make_historicjoa_response_payload()
    )
    responses = [
        first_response,
        HistoricJoaEndpoint.Response.model_validate(
            make_historicjoa_response_payload(
                continuation_token=first_response.next_token()
            )
        ),
    ]

    def fake_historic_joa(self, **_):
        return responses.pop(0)

    monkeypatch.setattr(USAJobsClient, "historic_joa", fake_historic_joa)

    client = USAJobsClient()
    iterator = client.historic_joa_pages()

    assert next(iterator)
    with pytest.raises(RuntimeError, match="duplicate continuation token"):
        next(iterator)


# test historic_joa_items
# ---


def test_historic_joa_items_yields_items_across_pages(
    monkeypatch: pytest.MonkeyPatch,
    make_historicjoa_response_payload,
    make_historicjoa_item,
) -> None:
    """Ensure historic_joa_items yields items and follows continuation tokens."""

    client = USAJobsClient()

    first_page = make_historicjoa_response_payload(continuation_token="TOKEN2")
    second_page = make_historicjoa_response_payload(
        items=[
            make_historicjoa_item(
                base=0,
                usajobsControlNumber=111222333,
                hiringAgencyCode="GSA",
                hiringAgencyName="General Services Administration",
                hiringDepartmentCode="GSA",
                hiringDepartmentName="General Services Administration",
                positionTitle="Systems Analyst",
            )
        ],
        continuation_token=None,
        total_count=3,
        page_size=1,
        next_url=None,
    )

    responses = [first_page, second_page]
    calls: list[dict[str, object]] = []

    def fake_historic(**call_kwargs):
        calls.append(call_kwargs)
        return HistoricJoaEndpoint.Response.model_validate(responses.pop(0))

    monkeypatch.setattr(client, "historic_joa", fake_historic)

    items = list(client.historic_joa_items(hiring_agency_codes="NASA"))

    assert [item.usajobs_control_number for item in items] == [
        123456789,
        987654321,
        111222333,
    ]
    assert len(calls) == 2
    assert "continuation_token" not in calls[0]
    assert calls[1]["continuation_token"] == "TOKEN2"


def test_historic_joa_items_respects_initial_token(
    monkeypatch: pytest.MonkeyPatch,
    make_historicjoa_response_payload,
) -> None:
    """Ensure historic_joa_items uses the supplied initial continuation token."""

    client = USAJobsClient()

    payload = make_historicjoa_response_payload(continuation_token=None)
    calls: list[dict[str, object]] = []

    def fake_historic(**call_kwargs):
        calls.append(call_kwargs)
        return HistoricJoaEndpoint.Response.model_validate(payload)

    monkeypatch.setattr(client, "historic_joa", fake_historic)

    items = list(client.historic_joa_items(continuation_token="SEED"))

    assert len(items) == len(payload["data"])
    assert calls[0]["continuation_token"] == "SEED"
