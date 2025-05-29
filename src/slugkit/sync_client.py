import httpx
import os
import logging
import functools

from typing import Any, Self, Generator, Callable

logger = logging.getLogger(__file__)


class SyncGenerator:
    def __init__(
        self,
        http_client: Callable[[], httpx.Client],
        *,
        batch_size: int = 10,
        limit: int | None = None,
    ):
        self._http_client = http_client
        self._batch_size = batch_size
        self._limit = limit

    def with_batch_size(self, batch_size: int) -> Self:
        return SyncGenerator(
            self._http_client,
            batch_size=batch_size,
            limit=self._limit,
        )

    def with_limit(self, limit: int) -> Self:
        return SyncGenerator(
            self._http_client,
            batch_size=self._batch_size,
            limit=limit,
        )

    def __call__(
        self,
        count: int = 1,
    ) -> list[str]:

        req = {}
        if count:
            req["count"] = count
        response = self._http_client().post(
            "/generate",
            json=req,
        )
        response.raise_for_status()
        return response.json()

    # TODO Maybe a stop signal?
    # TODO Maybe returne number of slugs generated?
    def generate(self) -> Generator[str, Any, int]:
        count = 0
        limit = self._limit
        batch_size = self._batch_size
        while True:
            if limit is not None:
                batch_size = min(batch_size, limit - count)
            if batch_size <= 0:
                break
            with self._http_client() as client:
                with client.stream(
                    "POST",
                    "/generate/stream",
                    json={"count": batch_size},
                ) as response:
                    response.raise_for_status()

                    for val in response.iter_lines():
                        stop = yield val.strip()
                        count += 1
                        if stop is not None:
                            break
                        if limit is not None and count >= limit:
                            break
        return count

    def reset(self) -> None:
        response = self._http_client().post("/reset")
        response.raise_for_status()

    def stats(self) -> dict[str, Any]:
        response = self._http_client().get("/stats")
        response.raise_for_status()
        return response.json()

    def __iter__(self) -> Generator[str, None, None]:
        return self.generate()


class PatternTester:
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
            "/generator/test",
            json=req,
        )
        return response.json()


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
    def generator(self) -> SyncGenerator:
        if not self._api_key:
            raise ValueError("Generator API is available only for authenticated projects")
        return SyncGenerator(self._http_client)

    @functools.cached_property
    def test(self) -> PatternTester:
        return PatternTester(self._http_client)
