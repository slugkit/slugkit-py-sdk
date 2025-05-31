import httpx

from typing import Any, Self, AsyncGenerator, Callable


class AsyncSlugGenerator:
    def __init__(
        self,
        http_client: Callable[[], httpx.AsyncClient],
        *,
        batch_size: int = 10,
        limit: int | None = None,
        dry_run: bool = False,
        sequence: int = 0,
    ):
        self._http_client = http_client
        self._batch_size = batch_size
        self._limit = limit
        self._dry_run = dry_run
        self._sequence = sequence

    def with_batch_size(self, batch_size: int) -> Self:
        return AsyncSlugGenerator(
            self._http_client,
            batch_size=batch_size,
            limit=self._limit,
            dry_run=self._dry_run,
            sequence=self._sequence,
        )

    def with_limit(self, limit: int) -> Self:
        return AsyncSlugGenerator(
            self._http_client,
            batch_size=self._batch_size,
            limit=limit,
            dry_run=self._dry_run,
            sequence=self._sequence,
        )

    def with_dry_run(self, dry_run: bool) -> Self:
        return AsyncSlugGenerator(
            self._http_client,
            batch_size=self._batch_size,
            limit=self._limit,
            dry_run=dry_run,
            sequence=self._sequence,
        )

    def starting_from(self, sequence: int) -> Self:
        return AsyncSlugGenerator(
            self._http_client,
            batch_size=self._batch_size,
            limit=self._limit,
            dry_run=self._dry_run,
            sequence=sequence,
        )

    async def __call__(self, count: int = 1) -> list[str]:
        req = {}
        if count:
            req["count"] = count
        if self._dry_run:
            req["sequence"] = self._sequence
        path = "/generate"
        if self._dry_run:
            path = "/nth"
        response = await self._http_client().post(path, json=req)
        response.raise_for_status()
        return response.json()

    async def generate(self) -> AsyncGenerator[str, Any]:
        count = 0
        limit = self._limit
        batch_size = self._batch_size
        sequence = self._sequence
        path = "/generate/stream"
        if self._dry_run:
            path = "/nth/stream"
        while True:
            if limit is not None:
                batch_size = min(batch_size, limit - count)
            if batch_size <= 0:
                break
            async with self._http_client() as client:
                if not self._dry_run:
                    req = {"count": batch_size}
                else:
                    req = {"count": batch_size, "sequence": sequence}
                async with client.stream(
                    "POST",
                    path,
                    json=req,
                ) as response:
                    response.raise_for_status()
                    async for val in response.aiter_lines():
                        stop = yield val.strip()
                        count += 1
                        if stop is not None:
                            break
                        if limit is not None and count >= limit:
                            break
            sequence += batch_size

    async def reset(self) -> None:
        response = await self._http_client().post("/reset")
        response.raise_for_status()

    async def stats(self) -> dict[str, Any]:
        response = await self._http_client().get("/stats")
        response.raise_for_status()
        return response.json()

    async def __aiter__(self) -> AsyncGenerator[str, None]:
        return self.generate()


class AsyncPatternTester:
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
        response = await self._http_client().post("/test", json=req)
        response.raise_for_status()
        return response.json()


class AsyncClient:
    def __init__(self, base_url: str, api_key: str | None = None):
        self.base_url = base_url
        self.api_key = api_key
