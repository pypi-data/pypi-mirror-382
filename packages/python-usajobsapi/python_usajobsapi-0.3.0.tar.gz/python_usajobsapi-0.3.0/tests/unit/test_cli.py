"""Unit tests for the CLI entry points."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, ClassVar

import pytest
from pydantic import BaseModel

from usajobsapi import cli


class DummyResponse(BaseModel):
    """Lightweight response model used to emulate client responses."""

    payload: dict[str, Any]


class FakeClient:
    """Test double for ``USAJobsClient`` used to capture CLI interactions."""

    instances: ClassVar[list["FakeClient"]] = []

    def __init__(
        self,
        url: str | None = "https://data.usajobs.gov",
        ssl_verify: bool = True,
        timeout: float | None = 60,
        auth_user: str | None = None,
        auth_key: str | None = None,
        session: Any = None,
    ) -> None:
        self.url = url
        self.ssl_verify = ssl_verify
        self.timeout = timeout
        self.auth_user = auth_user
        self.auth_key = auth_key
        self.session = session
        self.headers = {
            "Host": "data.usajobs.gov",
            "User-Agent": auth_user,
            "Authorization-Key": auth_key,
        }
        self.calls: list[tuple[str, dict[str, Any]]] = []
        FakeClient.instances.append(self)

    def _respond(self, method_name: str, params: dict[str, Any]) -> DummyResponse:
        recorded = dict(params)
        self.calls.append((method_name, recorded))
        return DummyResponse(payload={"method": method_name, "params": recorded})

    def announcement_text(self, **kwargs: Any) -> DummyResponse:
        return self._respond("announcement_text", kwargs)

    def search_jobs(self, **kwargs: Any) -> DummyResponse:
        return self._respond("search_jobs", kwargs)

    def historic_joa(self, **kwargs: Any) -> DummyResponse:
        return self._respond("historic_joa", kwargs)


@pytest.fixture()
def fake_client(monkeypatch: pytest.MonkeyPatch) -> type[FakeClient]:
    """Patch ``USAJobsClient`` with the fake client for a single test."""
    FakeClient.instances.clear()
    monkeypatch.setattr(cli, "USAJobsClient", FakeClient)
    return FakeClient


def test_parse_json_valid_object() -> None:
    """Ensure JSON parsing returns a dictionary."""
    payload = cli._parse_json('{"foo": "bar"}')
    assert payload == {"foo": "bar"}


@pytest.mark.parametrize(
    "raw",
    [
        "{invalid",
        '["not", "an", "object"]',
    ],
)
def test_parse_json_invalid_inputs(raw: str) -> None:
    """Invalid JSON strings raise argparse errors."""
    with pytest.raises(argparse.ArgumentTypeError):
        cli._parse_json(raw)


def test_build_parser_defaults() -> None:
    """The parser should expose the expected default values."""
    parser = cli._build_parser()
    args = parser.parse_args([cli.ACTIONS.TEXT.value])

    assert args.action == cli.ACTIONS.TEXT
    assert args.data == {}
    assert args.prettify is False
    assert args.ssl_verify is True
    assert args.timeout == cli.USAJobsClient().timeout
    assert args.auth_user is None
    assert args.auth_key is None


def test_build_parser_custom_overrides() -> None:
    """Custom overrides should populate their respective fields."""
    parser = cli._build_parser()
    payload = {"keyword": "python"}
    args = parser.parse_args(
        [
            cli.ACTIONS.SEARCH.value,
            "-d",
            json.dumps(payload),
            "--prettify",
            "--no-ssl-verify",
            "--timeout",
            "10",
            "-A",
            "user@example.com",
            "--auth-key",
            "secret",
        ]
    )

    assert args.action == cli.ACTIONS.SEARCH
    assert args.data == payload
    assert args.prettify is True
    assert args.ssl_verify is False
    assert args.timeout == 10.0
    assert args.auth_user == "user@example.com"
    assert args.auth_key == "secret"


def test_main_version_short_circuit(
    monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    """--version should print the package version and exit."""
    monkeypatch.setattr(sys, "argv", ["prog", "--version"], raising=False)

    with pytest.raises(SystemExit) as exc:
        cli.main()

    assert exc.value.code == 0
    out = capfd.readouterr().out.strip()
    assert out == cli.pkg_version


@pytest.mark.parametrize(
    ("action", "expected_method"),
    [
        (cli.ACTIONS.TEXT, "announcement_text"),
        (cli.ACTIONS.SEARCH, "search_jobs"),
        (cli.ACTIONS.HISTORIC, "historic_joa"),
    ],
)
def test_main_dispatches_to_expected_client_method(
    monkeypatch: pytest.MonkeyPatch,
    capfd: pytest.CaptureFixture[str],
    fake_client: type[FakeClient],
    action: cli.ACTIONS,
    expected_method: str,
) -> None:
    """Each CLI action should invoke the corresponding client method."""
    payload = {"query": action.value}
    monkeypatch.setattr(
        sys,
        "argv",
        ["prog", action.value, "-d", json.dumps(payload)],
        raising=False,
    )

    cli.main()

    out = capfd.readouterr().out.strip()
    assert json.loads(out) == {
        "payload": {"method": expected_method, "params": payload}
    }

    instance = fake_client.instances[-1]
    assert instance.calls[-1] == (expected_method, payload)


def test_main_prettify_outputs_indented_json(
    monkeypatch: pytest.MonkeyPatch,
    capfd: pytest.CaptureFixture[str],
    fake_client: type[FakeClient],
) -> None:
    """--prettify should request indented JSON output."""
    payload = {"foo": "bar"}
    monkeypatch.setattr(
        sys,
        "argv",
        ["prog", cli.ACTIONS.SEARCH.value, "-d", json.dumps(payload), "--prettify"],
        raising=False,
    )

    cli.main()
    out = capfd.readouterr().out

    assert out.startswith("{\n")
    assert '"payload"' in out

    instance = fake_client.instances[-1]
    assert instance.calls[-1] == ("search_jobs", payload)


def test_main_defaults_to_empty_payload(
    monkeypatch: pytest.MonkeyPatch,
    capfd: pytest.CaptureFixture[str],
    fake_client: type[FakeClient],
) -> None:
    """When no JSON payload is supplied the client receives an empty dict."""
    monkeypatch.setattr(
        sys,
        "argv",
        ["prog", cli.ACTIONS.SEARCH.value],
        raising=False,
    )

    cli.main()

    out = capfd.readouterr().out.strip()
    assert json.loads(out) == {"payload": {"method": "search_jobs", "params": {}}}

    instance = fake_client.instances[-1]
    assert instance.calls[-1] == ("search_jobs", {})
