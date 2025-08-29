import httpx
import os
import logging
import functools

from typing import Any, Generator, Callable
from .base import ApiClientBase, GeneratorBase, StatsItem, SeriesInfo

logger = logging.getLogger(__name__)


class SyncSlugGenerator(GeneratorBase):
    def __call__(
        self,
        count: int = 1,
    ) -> list[str]:
        req = self._get_request(count)
        path = self._get_path()

        self._logger.info(f"Requesting {count} slug(s)")
        response = self._http_client().post(
            path,
            json=req,
        )
        response.raise_for_status()
        return response.json()

    def stream(self) -> Generator[str, Any, int]:
        count = 0
        limit = self._limit
        batch_size = self._batch_size
        path = self._get_path(stream=True)
        sequence = self._sequence
        try:
            while True:
                if limit is not None:
                    batch_size = min(batch_size, limit - count)
                if batch_size <= 0:
                    break
                with self._http_client() as client:
                    req = self._get_request(batch_size, sequence)
                    self._logger.info(f"Requesting batch of {batch_size} slug(s)")
                    with client.stream(
                        "POST",
                        path,
                        json=req,
                    ) as response:
                        response.raise_for_status()

                        for val in response.iter_lines():
                            stop = yield val.strip()
                            count += 1
                            if stop is not None:
                                break
                            if limit is not None and count >= limit:
                                break
                sequence += batch_size
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                e.response.read()
                logger.error(f"Error: {e.response.text}")
                raise Exception(f"Error: {e.response.text}")
            raise
        except KeyboardInterrupt:
            ...
        self._logger.info(f"Generated {count} slugs")
        return count

    def __iter__(self) -> Generator[str, None, None]:
        return self.stream()


class RandomGenerator(GeneratorBase):
    def __init__(self, http_client: Callable[[], httpx.Client]):
        self._http_client = http_client

    def __call__(
        self,
        pattern: str,
        *,
        seed: str | None = None,
        sequence: int | None = None,
        count: int = 1,
    ) -> list[str]:
        req = {
            "pattern": pattern,
        }
        if seed:
            req["seed"] = seed
        if sequence:
            req["sequence"] = sequence
        if count:
            req["count"] = count
        response = self._http_client().post(
            self.FORGE_PATH,
            json=req,
        )
        response.raise_for_status()
        return response.json()


class SeriesClient(ApiClientBase):
    def __init__(self, httpx_client: Callable[[], httpx.Client]):
        super().__init__(httpx_client)

    def __getitem__(self, series_slug: str) -> SyncSlugGenerator:
        return self.mint.with_series(series_slug)

    def __call__(
        self,
        *,
        series_slug: str | None = None,
        batch_size: int = ApiClientBase.DEFAULT_BATCH_SIZE,
        limit: int | None = None,
        dry_run: bool = False,
        sequence: int = 0,
    ) -> SyncSlugGenerator:
        return SyncSlugGenerator(
            self._http_client,
            series_slug=series_slug,
            batch_size=batch_size,
            limit=limit,
            dry_run=dry_run,
            sequence=sequence,
        )

    @functools.cached_property
    def mint(self) -> SyncSlugGenerator:
        return self()

    @functools.cached_property
    def slice(self) -> SyncSlugGenerator:
        return self(dry_run=True)

    def stats(self) -> list[StatsItem]:
        response = self._http_client().get(self.STATS_PATH)
        response.raise_for_status()
        data = response.json()
        return [StatsItem.from_dict(item) for item in data]

    def info(self) -> SeriesInfo:
        response = self._http_client().get(self.SERIES_INFO_PATH)
        response.raise_for_status()
        data = response.json()
        return SeriesInfo.from_dict(data)

    def reset(self) -> None:
        response = self._http_client().post(self.RESET_PATH)
        response.raise_for_status()


class SyncClient:
    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        *,
        httpx_client_factory: Callable[[], Any] = httpx.Client,
        timeout: float = 10.0,
    ):
        if not base_url:
            base_url = os.getenv("SLUGKIT_BASE_URL")
        if not base_url:
            raise ValueError("SLUGKIT_BASE_URL is not set")
        if not api_key:
            api_key = os.getenv("SLUGKIT_API_KEY")
        self.base_url = base_url
        self._api_key = api_key
        self._httpx_client_factory = httpx_client_factory
        self._timeout = timeout

    def _http_client(self) -> httpx.Client:
        return self._httpx_client_factory(
            base_url=self.base_url,
            headers={"x-api-key": self._api_key},
            timeout=self._timeout,
        )

    @functools.cached_property
    def series(self) -> SeriesClient:
        if not self._api_key:
            raise ValueError("API key is required")
        return SeriesClient(self._http_client)

    @functools.cached_property
    def forge(self) -> RandomGenerator:
        if not self._api_key:
            raise ValueError("API key is required")
        return RandomGenerator(self._http_client)
