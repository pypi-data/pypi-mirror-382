# python-usajobsapi

[![PyPI][pypi-img]][pypi-lnk]
[![License][license-img]][license-lnk]
[![Tests][tests-img]][tests-lnk]
[![Python][python-img]][python-lnk]
[![Code Style][codestyle-img]][codestyle-lnk]
[![Coverage Status][codecov-img]][codecov-lnk]

`python-usajobsapi` is a typed Python wrapper for the [USAJOBS REST API](https://developer.usajobs.gov/). The project provides a clean interface for discovering and querying job postings using Python.

## Status

This project is under active development and its API may change. Changes to the [USAJOBS REST API documentation](https://developer.usajobs.gov/) are monitored and incorporated on a best-effort basis. Feedback and ideas are appreciated.

## Overview

The USAJOBS REST API exposes a large catalog of job opportunity announcements (JOAs) with a complex query surface. This project focuses on providing:

- Declarative endpoint definitions.
- Strongly typed request/query parameters and response models.
- Streaming helpers for paginating through large result sets.
- Normalization of data formats (e.g., date handling, booleans, payload serialization).

### Supported Endpoints

This package primarily aims to support searching and retrieval of active and past job listings. Coverage of all [documented endpoints](https://developer.usajobs.gov/api-reference/) will continue to be expanded.

Currently, the following endpoints are supported:

- [Job Search API](https://developer.usajobs.gov/api-reference/get-api-search) (`/api/Search`)
- [Historic JOA API](https://developer.usajobs.gov/api-reference/get-api-historicjoa) (`/api/HistoricJoa`)
- Planned in [#6](https://github.com/paddy74/python-usajobsapi/issues/6) - [Announcement Text API](https://developer.usajobs.gov/api-reference/get-api-joa) (`/api/HistoricJoa/AnnouncementText`)

## Installation

### From PyPI

```bash
pip install python-usajobsapi
```

or, with [astral-uv](https://docs.astral.sh/uv/):

```bash
uv add python-usajobsapi
```

### From source

```bash
git clone https://github.com/your-username/python-usajobsapi.git
cd python-usajobsapi
pip install .
```

## Quickstart

1. [Request USAJOBS API credentials](https://developer.usajobs.gov/APIRequest/Forms/DeveloperSignup) (Job Search API only).
2. Instatiate the client (`USAJobsClient`) with your `User-Agent` (email) and API key.
3. Perform a search:

```python
from usajobsapi import USAJobsClient

client = USAJobsClient(auth_user="name@example.com", auth_key="YOUR_API_KEY")
response = client.search_jobs(keyword="data scientist", location_names=["Atlanta", "Georgia"])

for job in response.jobs():
    print(job.position_title)
```

### Pagination

### Handling pagination

Use streaming helpers to to iterate through multiple pages or individual result items without needing to worry about pagination:

```python
for job in client.search_jobs_items(keyword="cybersecurity", results_per_page=100):
    if "Remote" in (job.position_location_display or ""):
        print(job.position_title, job.organization_name)
```

## Developer Guide

Set up a development environment with [`uv`](https://docs.astral.sh/uv/):

```bash
uv sync --all-extras --all-groups
uv run pytest tests
uv run ruff check
uv run ruff format
```

### Key Development Principles

- Keep Pydantic models exhaustive and prefer descriptive field metadata so that auto-generated docs remain informative.
- Maintain 100% passing tests, at least 80% test coverage, formatting, and linting before opening a pull request.
- Update docstrings alongside code changes to keep the generated reference accurate.

### Document Generation

Documentation is generated using [MkDocs](https://www.mkdocs.org/). The technical reference surfaces the reStructuredText style docstrings from the package's source code.

```bash
uv sync --group docs

# Run the development server
uv run mkdocs serve -f mkdocs/mkdocs.yaml
# Build the static site
uv run mkdocs build -f mkdocs/mkdocs.yaml
```

## Contributing

Contributions are welcome! To get started:

1. Fork the repository and create a new branch.
2. Install development dependencies (see the [developer guide](#developer-guide)).
3. Add or update tests together with your change.
4. Run the full test, linting, and formatting suite locally.
5. Submit a pull request describing your changes and referencing any relevant issues.

For major changes, open an issue first to discuss your proposal.

## Design

The software design architecture prioritizes composability and strong typing, ensuring that it is straightforward to add/update endpoints and generate documentation from docstrings.

- **Client session management**: `USAJobsClient` wraps a configurable `requests.Session` to reuse connections and centralize authentication headers.
- **Declarative endpoints**: Each USAJOBS endpoint is expressed as a Pydantic model with nested `Params` and `Response` classes, providing validation, serialization helpers, and rich metadata for documentation.
- **Pagination helpers**: Iterators (`search_jobs_pages` and `search_jobs_items`) encapsulate pagination logic and expose idiomatic Python iterators so users focus on data consumption, not page math.
- **Shared utilities**: Shared utilities handle API-specific normalization (e.g., date parsing, alias mapping) so endpoint models stay declarative and thin.

## License

Distributed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html). See [LICENSE](LICENSE) for details.

## Contact

Questions or issues? Please open an issue on the repository's issue tracker.

<!-- Badges -->

[pypi-lnk]: https://pypi.org/p/python-usajobsapi
[pypi-img]: https://img.shields.io/pypi/v/python-usajobsapi.svg
[tests-lnk]: https://github.com/paddy74/python-usajobsapi/actions
[tests-img]: https://img.shields.io/github/actions/workflow/status/paddy74/python-usajobsapi/ci.yaml?logo=github&label=tests&branch=master
[codecov-lnk]: https://codecov.io/github/paddy74/python-usajobsapi
[codecov-img]: https://codecov.io/github/paddy74/python-usajobsapi/graph/badge.svg?token=IH3MTBANTT
[python-lnk]: https://img.shields.io/pypi/pyversions/python-usajobsapi.svg
[python-img]: https://pypi.python.org/pypi/python-usajobsapi
[codestyle-lnk]: https://docs.astral.sh/ruff
[codestyle-img]: https://img.shields.io/badge/code%20style-ruff-000000.svg
[license-lnk]: ./LICENSE
[license-img]: https://img.shields.io/pypi/l/python-usajobsapi?color=light-green&logo=gplv3&logoColor=white
