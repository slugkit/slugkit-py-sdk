import httpx
import os
import logging

from typing import Any, AsyncGenerator, Callable

from .base import (
    DictionaryInfo,
    PaginatedTags,
    GeneratorBase,
    PatternInfo,
    StatsItem,
    SeriesInfo,
    KeyInfo,
    SubscriptionFeatures,
    retry_with_backoff,
    SlugKitConnectionError,
    SlugKitAuthenticationError,
    SlugKitClientError,
    SlugKitServerError,
    SlugKitValidationError,
    SlugKitTimeoutError,
    SlugKitQuotaError,
    SlugKitConfigurationError,
    SlugKitRateLimitError,
    ErrorContext,
    get_error_recovery_suggestions,
    categorize_error,
    handle_http_error,
    Endpoints,
)


class AsyncSlugGenerator(GeneratorBase):
    async def __call__(self, count: int = 1) -> list[str]:
        req = self._get_request(count)
        path = self._get_path()
        client = await self._http_client()
        self._logger.info(f"Requesting {count} slug(s)")
        try:
            response = await client.post(path, json=req)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise handle_http_error(e, "mint_slugs", path)

    async def stream(self) -> AsyncGenerator[str, Any]:
        count = 0
        limit = self._limit
        batch_size = self._batch_size
        sequence = self._sequence
        path = self._get_path(stream=True)

        try:
            while True:
                if limit is not None and count >= limit:
                    break

                current_batch_size = min(batch_size, limit - count) if limit is not None else batch_size
                if current_batch_size <= 0:
                    break

                client = await self._http_client()
                async with client:
                    req = self._get_request(current_batch_size, sequence)
                    self._logger.info(f"Requesting batch of {current_batch_size} slug(s)")
                    # Get the streaming response and use it as a context manager
                    stream_response = client.stream(
                        "POST",
                        path,
                        json=req,
                    )
                    async with stream_response as response:
                        response.raise_for_status()
                        self._logger.debug(f"Received batch of {current_batch_size} slug(s)")
                        # Get the async iterator and use it
                        async_lines = response.aiter_lines()
                        async for val in async_lines:
                            yield val.strip()
                            count += 1
                            if limit is not None and count >= limit:
                                return
                sequence += current_batch_size
        except httpx.HTTPStatusError as e:
            raise handle_http_error(e, "stream_slugs", path)
        except KeyboardInterrupt:
            return

    def __aiter__(self) -> AsyncGenerator[str, None]:
        return self.stream()


class AsyncRandomGenerator(GeneratorBase):
    def __init__(self, http_client: Callable[[], httpx.AsyncClient]):
        self._http_client = http_client

    async def __call__(
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
        client = await self._http_client()
        try:
            response = await client.post(Endpoints.FORGE.value, json=req)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise handle_http_error(e, "forge_slugs", Endpoints.FORGE.value, pattern=pattern)

    async def pattern_info(self, pattern: str) -> PatternInfo:
        client = await self._http_client()
        try:
            response = await client.post(Endpoints.PATTERN_INFO.value, json={"pattern": pattern})
            response.raise_for_status()
            data = response.json()
            return PatternInfo.from_dict(data)
        except httpx.HTTPStatusError as e:
            raise handle_http_error(e, "pattern_info", Endpoints.PATTERN_INFO.value, pattern=pattern)

    async def dictionary_info(self) -> list[DictionaryInfo]:
        client = await self._http_client()
        try:
            response = await client.get(Endpoints.DICTIONARY_INFO.value)
            response.raise_for_status()
            data = response.json()
            return [DictionaryInfo.from_dict(item) for item in data]
        except httpx.HTTPStatusError as e:
            raise handle_http_error(e, "dictionary_info", Endpoints.DICTIONARY_INFO.value)

    async def dictionary_tags(self, kind: str, *, limit: int = 100, offset: int = 0) -> PaginatedTags:
        client = await self._http_client()
        try:
            response = await client.get(f"{Endpoints.DICTIONARY_TAGS.value}/{kind}?limit={limit}&offset={offset}")
            response.raise_for_status()
            data = response.json()
            return PaginatedTags.from_dict(data)
        except httpx.HTTPStatusError as e:
            raise handle_http_error(e, "dictionary_tags", Endpoints.DICTIONARY_TAGS.value)


class AsyncSeriesClient:
    def __init__(
        self,
        http_client: Callable[[], httpx.AsyncClient],
        base_url: str,
        api_key: str,
        series_slug: str | None = None,
    ):
        self._http_client = http_client
        self.base_url = base_url
        self._api_key = api_key
        self._series: str | None = series_slug
        self._logger = logging.getLogger(f"{self.__class__.__name__}")

    def __getitem__(self, series_slug: str) -> AsyncSlugGenerator:
        return self.with_series(series_slug)

    def with_series(self, series_slug: str) -> "AsyncSeriesClient":
        return AsyncSeriesClient(
            self._http_client,
            self.base_url,
            self._api_key,
            series_slug,
        )

    @property
    def mint(self) -> AsyncSlugGenerator:
        return AsyncSlugGenerator(self._http_client, series_slug=self._series)

    @property
    def slice(self) -> AsyncSlugGenerator:
        return AsyncSlugGenerator(self._http_client, series_slug=self._series).with_dry_run()

    @retry_with_backoff(max_attempts=3, base_delay=1.0)
    async def stats(self) -> list[StatsItem]:
        try:
            client = await self._http_client()
            req = {}
            if self._series:
                req["series"] = self._series
            response = await client.post(Endpoints.STATS.value, json=req)
            response.raise_for_status()
            data = response.json()
            return [StatsItem.from_dict(item) for item in data]
        except httpx.HTTPStatusError as e:
            raise handle_http_error(e, "series_stats", Endpoints.STATS.value)

    @retry_with_backoff(max_attempts=3, base_delay=1.0)
    async def info(self) -> SeriesInfo:
        try:
            client = await self._http_client()
            req = {}
            if self._series:
                req["series"] = self._series
            response = await client.post(Endpoints.SERIES_INFO.value, json=req)
            response.raise_for_status()
            data = response.json()
            return SeriesInfo.from_dict(data)
        except httpx.HTTPStatusError as e:
            raise handle_http_error(e, "series_info", Endpoints.SERIES_INFO.value)

    @retry_with_backoff(max_attempts=3, base_delay=1.0)
    async def list(self) -> dict[str, str]:
        try:
            client = await self._http_client()
            response = await client.get(Endpoints.SERIES_LIST.value)
            response.raise_for_status()
            data = response.json()
            return data
        except httpx.HTTPStatusError as e:
            raise handle_http_error(e, "series_list", Endpoints.SERIES_LIST.value)

    @retry_with_backoff(max_attempts=3, base_delay=1.0)
    async def create(self, name: str, pattern: str) -> SeriesInfo:
        try:
            client = await self._http_client()
            response = await client.post(Endpoints.SERIES_CREATE.value, json={"name": name, "pattern": pattern})
            response.raise_for_status()
            data = response.json()
            return SeriesInfo.from_dict(data)
        except httpx.HTTPStatusError as e:
            raise handle_http_error(e, "series_create", Endpoints.SERIES_CREATE.value)

    @retry_with_backoff(max_attempts=3, base_delay=1.0)
    async def update(self, name: str, pattern: str) -> SeriesInfo:
        try:
            client = await self._http_client()
            response = await client.put(
                Endpoints.SERIES_UPDATE.value, json={"series": self._series, "name": name, "pattern": pattern}
            )
            response.raise_for_status()
            data = response.json()
            return SeriesInfo.from_dict(data)
        except httpx.HTTPStatusError as e:
            raise handle_http_error(e, "series_update", Endpoints.SERIES_UPDATE.value)

    @retry_with_backoff(max_attempts=3, base_delay=1.0)
    async def delete(self) -> None:
        try:
            client = await self._http_client()
            response = await client.request(
                "DELETE",
                Endpoints.SERIES_DELETE.value,
                json={"series": self._series},
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise handle_http_error(e, "series_delete", Endpoints.SERIES_DELETE.value)

    @retry_with_backoff(max_attempts=3, base_delay=1.0)
    async def reset(self) -> None:
        try:
            client = await self._http_client()
            req = {}
            if self._series:
                req["series"] = self._series
            response = await client.post(Endpoints.RESET.value, json=req)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise handle_http_error(e, "series_reset", Endpoints.RESET.value)


class AsyncClient:
    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        *,
        httpx_client_factory: Callable[[], Any] = httpx.AsyncClient,
        timeout: float = 10.0,
    ):
        if not base_url:
            base_url = os.getenv("SLUGKIT_BASE_URL")
        if not base_url:
            raise ValueError("SLUGKIT_BASE_URL is not set")
        if not api_key:
            api_key = os.getenv("SLUGKIT_API_KEY", None)
        self.base_url = base_url
        self._api_key = api_key
        self._httpx_client_factory = httpx_client_factory
        self._timeout = timeout

    async def _http_client(self) -> httpx.AsyncClient:
        return self._httpx_client_factory(
            base_url=self.base_url,
            headers={"x-api-key": self._api_key},
            timeout=self._timeout,
        )

    def _create_error_context(self, operation: str, endpoint: str = None, **kwargs) -> ErrorContext:
        """Create error context for better error reporting."""
        return ErrorContext(operation=operation, endpoint=endpoint, base_url=self.base_url, **kwargs)

    @retry_with_backoff(max_attempts=3, base_delay=1.0)
    async def ping(self) -> None:
        try:
            client = await self._http_client()
            response = await client.get(Endpoints.PING.value)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise handle_http_error(e, "ping", Endpoints.PING.value)

    @retry_with_backoff(max_attempts=3, base_delay=1.0)
    async def key_info(self) -> KeyInfo:
        if not self._api_key:
            raise ValueError("API key is required")
        try:
            client = await self._http_client()
            response = await client.post(Endpoints.KEY_INFO.value)
            response.raise_for_status()
            data = response.json()
            return KeyInfo.from_dict(data)
        except httpx.HTTPStatusError as e:
            raise handle_http_error(e, "key_info", Endpoints.KEY_INFO.value)

    @retry_with_backoff(max_attempts=3, base_delay=1.0)
    async def limits(self) -> SubscriptionFeatures:
        """Get the organisation's subscription limits and features.

        Returns:
            SubscriptionFeatures: The subscription limits and features
        """
        if not self._api_key:
            raise ValueError("API key is required")
        try:
            client = await self._http_client()
            response = await client.get(Endpoints.LIMITS.value)
            response.raise_for_status()
            data = response.json()
            return SubscriptionFeatures.from_dict(data)
        except httpx.HTTPStatusError as e:
            raise handle_http_error(e, "limits", Endpoints.LIMITS.value)

    @property
    def api_key(self) -> str | None:
        """Get the API key."""
        return self._api_key

    @property
    def series(self) -> AsyncSeriesClient:
        if not self._api_key:
            raise ValueError("API key is required")
        return AsyncSeriesClient(self._http_client, self.base_url, self._api_key)

    @property
    def forge(self) -> AsyncRandomGenerator:
        if not self._api_key:
            raise ValueError("API key is required")
        return AsyncRandomGenerator(self._http_client)
