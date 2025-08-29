import httpx
import logging
from enum import Enum
from typing import Any, Callable, Self
from pydantic import BaseModel


class EventType(Enum):
    """Enum for event types in stats responses."""

    FORGE = "forge"
    MINT = "mint"
    SLICE = "slice"
    RESET = "reset"


class DatePart(Enum):
    """Enum for date parts in stats responses."""

    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    TOTAL = "total"


class StatsItem(BaseModel):
    """Pydantic model representing a single stats item from the API response."""

    event_type: str
    date_part: str
    total_count: int
    request_count: int
    total_duration_us: int
    avg_duration_us: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StatsItem":
        """Create a StatsItem instance from a dictionary (compat helper)."""
        return cls.model_validate(data)

    def to_dict(self) -> dict[str, Any]:
        """Convert the StatsItem to a dictionary (compat helper)."""
        return self.model_dump()


class SeriesInfo(BaseModel):
    """Pydantic model representing series information from the API response."""

    slug: str
    org_slug: str
    pattern: str
    max_pattern_length: int
    capacity: str
    generated_count: str
    mtime: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SeriesInfo":
        """Create a SeriesInfo instance from a dictionary (compat helper)."""
        return cls.model_validate(data)

    def to_dict(self) -> dict[str, Any]:
        """Convert the SeriesInfo to a dictionary (compat helper)."""
        return self.model_dump()


class ApiClientBase:
    MINT_PATH = "/gen/mint"
    SLICE_PATH = "/gen/slice"
    FORGE_PATH = "/gen/forge"
    RESET_PATH = "/gen/reset"
    STATS_PATH = "/gen/stats/latest"
    SERIES_INFO_PATH = "/gen/series-info"

    DEFAULT_BATCH_SIZE = 100000

    def __init__(self, http_client: Callable[[], httpx.Client]):
        self._http_client = http_client
        self._logger = logging.getLogger(f"{self.__class__.__name__}")


class GeneratorBase(ApiClientBase):
    def __init__(
        self,
        http_client: Callable[[], httpx.Client],
        *,
        series_slug: str | None = None,
        batch_size: int = ApiClientBase.DEFAULT_BATCH_SIZE,
        limit: int | None = None,
        dry_run: bool = False,
        sequence: int = 0,
    ):
        super().__init__(http_client)
        self._series_slug = series_slug
        self._batch_size = batch_size
        self._limit = limit
        self._dry_run = dry_run
        self._sequence = sequence

    def with_series(self, series_slug: str) -> Self:
        return self.__class__(
            self._http_client,
            series_slug=series_slug,
            batch_size=self._batch_size,
            limit=self._limit,
            dry_run=self._dry_run,
            sequence=self._sequence,
        )

    def with_batch_size(self, batch_size: int) -> Self:
        return self.__class__(
            self._http_client,
            series_slug=self._series_slug,
            batch_size=batch_size,
            limit=self._limit,
            dry_run=self._dry_run,
            sequence=self._sequence,
        )

    def with_limit(self, limit: int) -> Self:
        return self.__class__(
            self._http_client,
            series_slug=self._series_slug,
            batch_size=self._batch_size,
            limit=limit,
            dry_run=self._dry_run,
            sequence=self._sequence,
        )

    def with_dry_run(self) -> Self:
        return self.__class__(
            self._http_client,
            series_slug=self._series_slug,
            batch_size=self._batch_size,
            limit=self._limit,
            dry_run=True,
            sequence=self._sequence,
        )

    def starting_from(self, sequence: int) -> Self:
        return self.__class__(
            self._http_client,
            series_slug=self._series_slug,
            batch_size=self._batch_size,
            limit=self._limit,
            dry_run=self._dry_run,
            sequence=sequence,
        )

    def _get_request(self, count: int, sequence: int | None = None) -> dict[str, Any]:
        req = {"count": count}
        if self._dry_run and sequence is not None:
            req["sequence"] = sequence
        if self._series_slug:
            req["series"] = self._series_slug
        return req

    def _get_path(self, stream: bool = False) -> str:
        path = self.MINT_PATH
        if self._dry_run:
            path = self.SLICE_PATH
        if stream:
            path = f"{path}/stream"
        return path
