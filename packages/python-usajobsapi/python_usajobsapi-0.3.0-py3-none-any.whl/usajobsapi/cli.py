"""
Command line interface for the python-usajobsapi package.

This module powers the `usajobsapi` executable, so that a user can query the exposed endpoints from the command line.
"""

from __future__ import annotations

import argparse
import json
import sys
from enum import StrEnum
from typing import Any

from pydantic import BaseModel

from usajobsapi._version import __title__ as pkg_title
from usajobsapi._version import __version__ as pkg_version
from usajobsapi.client import USAJobsClient


class ACTIONS(StrEnum):
    TEXT = "announcementtext"
    SEARCH = "search"
    HISTORIC = "historicjoa"


def _parse_json(value: str) -> dict[str, Any]:
    """Parse JSON-encoded argument data."""
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise argparse.ArgumentTypeError(f"Invalid JSON payload: {exc}") from exc

    if not isinstance(parsed, dict):
        raise argparse.ArgumentTypeError(
            "JSON payload must decode to an object (dict)."
        )

    return parsed


def _build_parser() -> argparse.ArgumentParser:
    """Create the top-level argument parser for the CLI."""
    client_defaults = USAJobsClient()
    parser = argparse.ArgumentParser(
        prog=pkg_title,
        description="USAJOBS REST API Command Line Interface.",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {pkg_version}",
        help="Display the package version.",
    )

    parser.add_argument(
        "action",
        type=ACTIONS,
        choices=list(ACTIONS),
        help="Endpoint to query.",
    )
    parser.add_argument(
        "-d",
        "--data",
        type=_parse_json,
        default={},
        metavar="JSON",
        help="JSON-encoded parameters to pass to the selected endpoint.",
    )
    parser.add_argument(
        "--prettify", action="store_true", help="Prettify the JSON output."
    )

    parser.add_argument(
        "--no-ssl-verify",
        dest="ssl_verify",
        action="store_false",
        default=client_defaults.ssl_verify,
        help="Disable TLS certificate verification.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=client_defaults.timeout,
        metavar="SECONDS",
        help="Request timeout in seconds. Defaults to the client default.",
    )

    parser.add_argument(
        "-A",
        "--user-agent",
        dest="auth_user",
        default=client_defaults.headers["User-Agent"],
        metavar="EMAIL",
        help="Email address associated with the API key (User-Agent header).",
    )
    parser.add_argument(
        "--auth-key",
        dest="auth_key",
        default=client_defaults.headers["Authorization-Key"],
        metavar="KEY",
        help="API key used for authenticated requests.",
    )

    return parser


def main() -> None:
    if "--version" in sys.argv:
        print(pkg_version)
        sys.exit(0)

    parser = _build_parser()
    args = parser.parse_args()

    client = USAJobsClient(
        ssl_verify=args.ssl_verify,
        timeout=args.timeout,
        auth_user=args.auth_user,
        auth_key=args.auth_key,
    )

    action = args.action
    if not action:
        sys.exit(0)

    resp: BaseModel | None = None
    if action == ACTIONS.TEXT:
        resp = client.announcement_text(**args.data)
    elif action == ACTIONS.SEARCH:
        resp = client.search_jobs(**args.data)
    elif action == ACTIONS.HISTORIC:
        resp = client.historic_joa(**args.data)

    if not resp:
        sys.exit(1)

    if args.prettify:
        print(resp.model_dump_json(indent=2))
    else:
        print(resp.model_dump_json())
