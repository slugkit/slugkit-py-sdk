# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SlugKit Python SDK is a client library for generating human-readable, unique identifiers using the SlugKit.dev service. The SDK provides both synchronous and asynchronous clients, a CLI tool, and an MCP (Model Context Protocol) server for AI assistant integration.

## Development Commands

### Build and Publish
```bash
make build              # Build distribution packages with hatchling
make publish            # Build and publish to PyPI using twine
```

### Testing
```bash
make test               # Run tests with pytest
make test-verbose       # Run tests with verbose output
make test-coverage      # Run tests with coverage report
make install-test-deps  # Install test dependencies with uv
```

### Docker (MCP Server)
```bash
make build-mcp-image           # Build MCP server docker image for current architecture
make build-mcp-images          # Build for all architectures (amd64, arm64)
make push-mcp-images           # Push images and create multi-arch manifest
```

### Running Individual Tests
```bash
uv run --group test pytest tests/test_sync_client.py         # Run specific test file
uv run --group test pytest tests/test_async_client.py::TestAsyncClient::test_mint  # Run specific test
```

### CLI Usage
```bash
slugkit mint                    # Generate IDs
slugkit forge "pattern"         # Test patterns
slugkit stats                   # Get statistics
slugkit limits                  # Get subscription limits
slugkit-mcp                     # Start MCP server
```

## Architecture

### Client Architecture

The SDK follows a layered architecture with clear separation between sync and async implementations:

1. **Base Layer** (`base.py`)
   - Defines all Pydantic models (`StatsItem`, `SeriesInfo`, `PatternInfo`, `DictionaryInfo`, `KeyInfo`, `SubscriptionFeatures`, etc.)
   - Contains `GeneratorBase` class with shared generator configuration logic
   - Implements comprehensive error handling with retry logic and exponential backoff
   - Defines API endpoint constants in `Endpoints` enum
   - All error types inherit from `SlugKitError` base class

2. **Client Implementations**
   - `SyncClient` (`sync_client.py`) - Uses `httpx.Client` for synchronous operations
   - `AsyncClient` (`async_client.py`) - Uses `httpx.AsyncClient` for async/await operations
   - Both clients expose identical APIs through `series` and `forge` properties

3. **Generator Pattern**
   - `SyncSlugGenerator` and `AsyncSlugGenerator` provide fluent configuration API
   - Methods like `with_limit()`, `with_batch_size()`, `with_dry_run()`, `starting_from()` return new configured instances
   - Support both batch generation via `__call__()` and streaming via `__iter__()` / `__aiter__()`
   - `mint` property generates real IDs, `slice` property previews without consuming

4. **Series Management**
   - `SeriesClient` and `AsyncSeriesClient` handle series-specific operations
   - Support dict-like access: `client.series["series-slug"]`
   - Operations: `mint`, `slice`, `stats`, `info`, `list`, `create`, `update`, `delete`, `reset`

5. **Pattern Testing (Forge)**
   - `RandomGenerator` and `AsyncRandomGenerator` test patterns without series
   - Methods: `__call__()` for generation, `pattern_info()`, `dictionary_info()`, `dictionary_tags()`

### Error Handling

Comprehensive error handling system with:
- Custom exception hierarchy: `SlugKitConnectionError`, `SlugKitAuthenticationError`, `SlugKitValidationError`, `SlugKitTimeoutError`, `SlugKitRateLimitError`, `SlugKitQuotaError`, etc.
- `ErrorContext` dataclass for rich error information
- Automatic retry with exponential backoff via `@retry_with_backoff` decorator
- Error categorisation and recovery suggestions
- `handle_http_error()` converts httpx exceptions to SlugKit exceptions

#### Rate Limiting

The SDK implements intelligent rate limit handling:
- Extracts rate limit headers: `X-Slug-Rate-Limit-Reason`, `X-Slug-Retry-After`, `X-Slug-Rpm-Remaining`, `X-Slug-Daily-Remaining`, `X-Slug-Monthly-Remaining`, `X-Slug-Lifetime-Remaining`
- `SlugKitRateLimitError` includes quota information and formatted retry-after times
- Respects server-provided `retry_after` in backoff calculations
- Three-tier retry strategy:
  - **Retryable (token bucket)**: `rate-limit-exceeded` (RPM), `daily-limit-exceeded` - accurate retry-after
  - **Non-retryable (permanent)**: `not-available`, `request-size-exceeded` - won't succeed on retry
  - **Non-retryable (long-term)**: `monthly-limit-exceeded`, `lifetime-limit-exceeded` - no accurate retry-after
  - **Non-retryable (server)**: `redis-error` - server issue
- Context-specific error suggestions guide users to appropriate actions

### MCP Server

Located in `src/slugkit/mcp/server.py`:
- Built using FastMCP framework
- Exposes SlugKit functionality to AI assistants (Claude Desktop, Cursor, Warp)
- Supports both API key from environment and per-request headers
- Resources: documentation files from `src/slugkit/data/`
- Tools: all SlugKit API operations (`mint`, `forge`, `stats`, `pattern_info`, etc.)

## Key Implementation Details

### HTTP Client Factory Pattern

Both clients use a factory pattern for HTTP client creation:
- `SyncClient` creates new `httpx.Client` instances for each request
- `AsyncClient` creates new `httpx.AsyncClient` instances for each request
- Base URL and API key configured at client initialisation
- API key passed via `x-api-key` header

### Streaming Implementation

- Sync streaming uses `httpx.Client.stream()` context manager with `iter_lines()`
- Async streaming uses `httpx.AsyncClient.stream()` context manager with `aiter_lines()`
- Streams fetch batches of slugs (default batch size: 100,000)
- Support for limits and starting sequences

### Configuration Precedence

1. Explicit parameters passed to client constructor
2. Environment variables (`SLUGKIT_BASE_URL`, `SLUGKIT_API_KEY`)
3. Defaults (base_url: required, timeout: 10.0s)

## Testing Notes

- Tests use `pytest` with `pytest-asyncio` for async tests
- `conftest.py` provides shared fixtures
- Tests mock httpx responses to avoid hitting real API
- All test files follow `test_*.py` naming convention
- Async test mode configured in `pyproject.toml`: `asyncio_mode = "auto"`

## Documentation Files

Pattern documentation and examples stored in `src/slugkit/data/`:
- `pattern-syntax-reference.md` - Pattern language syntax
- `pattern-examples.md` - Example patterns
- `pattern-grammar.ebnf` - Formal grammar
- `dictionary-and-tag-reference.md` - Available dictionaries and tags
- `quick-start-guide.md` - Getting started guide

These files are packaged with the distribution and accessible via MCP server resources.
