"""Top-level package for the USAJOBS REST API wrapper."""

from usajobsapi._version import (
    __author__,
    __copyright__,
    __email__,
    __license__,
    __title__,
    __version__,
)
from usajobsapi.client import USAJobsClient

__all__: list[str] = [
    "__author__",
    "__copyright__",
    "__email__",
    "__license__",
    "__title__",
    "__version__",
    "USAJobsClient",
]
