"""
Wrapper for USAJOBS REST API endpoints.

Each endpoint exposes declarative `Params` and `Response` models so you can validate queries and parse responses without hand-written schemas.
"""

from .announcementtext import AnnouncementTextEndpoint
from .historicjoa import HistoricJoaEndpoint
from .search import SearchEndpoint

__all__: list[str] = [
    "AnnouncementTextEndpoint",
    "HistoricJoaEndpoint",
    "SearchEndpoint",
]
