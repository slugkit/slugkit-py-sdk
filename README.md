# SlugKit Python SDK

A Python SDK for generating human-readable IDs using [SlugKit.dev](https://dev.slugkit.dev) service.

Please see [SlugKit documentation](https://dev.slugkit.dev/docs) for information
on creating series and obtaining API keys.

## Installation

```bash
pip install slugkit-py-sdk
```

## API Overview

The SDK provides a comprehensive interface to generate human-readable IDs, test patterns, and manage generator state.

### Basic Usage

```python
from slugkit import SyncClient

# Initialize the client
client = SyncClient(
    base_url="https://dev.slugkit.dev/api/v1",
    api_key="your-api-key"
)

# Generate a single ID
id = client.series.mint()[0]

# Generate multiple IDs
ids = client.series.mint(count=5)

# Get generator stats
stats = client.series.stats()

# Get series information
series_info = client.series.info()

# Get list of available series
series_list = client.series.list()

# Get subscription limits and features
limits = client.limits()

# Reset the generator
client.series.reset()
```

### Advanced Generator Configuration

```python
# Configure generator with limits and batch sizes
generator = client.series.mint.with_limit(100).with_batch_size(10)

# Start from a specific sequence
generator = generator.starting_from(1000)

# Use dry-run mode (for testing)
generator = generator.with_dry_run()

# Generate IDs with configuration
ids = list(generator)
```

### Pattern Testing (Forge)

```python
# Test a pattern with various options
ids = client.forge(
    pattern="{adjective}-{noun}-{number:3d}",
    seed="optional-seed",
    sequence=1,
    count=5
)

# Get pattern information
pattern_info = client.forge.pattern_info("{adjective}-{noun}-{number:3d}")

# Get dictionary information
dict_info = client.forge.dictionary_info()

# Get dictionary tags
dict_tags = client.forge.dictionary_tags()

# Use different pattern types
ids = client.forge(
    pattern="simple-{noun}-{number:2,hex}",
    count=3
)
```

### Series Management

```python
# Access a specific series
series_generator = client.series["series-slug"]

# Generate IDs for specific series
ids = series_generator(count=10)

# Get stats for specific series
stats = series_generator.stats()

# Get series info for specific series
series_info = series_generator.series_info()
```

### Async Usage

The SDK also provides an async client for use with async/await code:

```python
import asyncio
from slugkit import AsyncClient

async def main():
    # Initialize the async client
    client = AsyncClient(
        base_url="https://dev.slugkit.dev/api/v1",
        api_key="your-api-key"
    )

    # Generate a single ID
    id = await client.series.mint()[0]

    # Generate multiple IDs
    ids = await client.series.mint(count=5)

    # Get generator stats
    stats = await client.series.stats()

    # Get series information
    series_info = await client.series.info()

    # Get list of available series
    series_list = await client.series.list()

    # Get subscription limits and features
    limits = await client.limits()

    # Reset the generator
    await client.series.reset()

    # Test a pattern
ids = await client.forge(
    pattern="{adjective}-{noun}-{number:3d}",
    seed="optional-seed",
    sequence=1,
    count=5
)

# Get pattern information
pattern_info = await client.forge.pattern_info("{adjective}-{noun}-{number:3d}")

# Get dictionary information
dict_info = await client.forge.dictionary_info()

# Get dictionary tags
dict_tags = await client.forge.dictionary_tags()

    # Stream IDs asynchronously
    async for id in client.series.mint:
        print(id)

# Run the async code
asyncio.run(main())
```

## Command Line Interface

The SDK includes a command-line interface for easy usage:

### Generate IDs

```bash
# Generate a single ID
slugkit mint

# Generate multiple IDs
slugkit mint 5

# Generate IDs with custom batch size
slugkit mint 10 --batch-size 2
```

### Test Patterns

```bash
# Test a pattern
slugkit forge "your-pattern"

# Test with specific seed and sequence
slugkit forge "your-pattern" --seed "my-seed" --sequence 1

# Generate multiple test IDs
slugkit forge "your-pattern" --count 5

# Validate a pattern and get information
slugkit validate "your-pattern"
```

### Generator Management

```bash
# Get generator stats
slugkit stats

# Get list of available series
slugkit series-list

# Get series information
slugkit series-info

# Get subscription limits and features
slugkit limits

# Get subscription limits in JSON format
slugkit limits --output-format json

# Reset the generator
slugkit reset
```

### Configuration

The CLI can be configured using environment variables or command-line options:

```bash
# Set base URL
export SLUGKIT_BASE_URL="https://dev.slugkit.dev/api/v1"

# Set API key
export SLUGKIT_API_KEY="your-api-key"

# Or use command-line options
slugkit --base-url "https://dev.slugkit.dev/api/v1" --api-key "your-api-key" mint
```

### Output Format

The CLI supports different output formats:

```bash
# Text output (default)
slugkit mint

# JSON output
slugkit mint --output-format json
```

## Data Types

The SDK provides structured data types for API responses:

### StatsItem

Represents generator statistics:

```python
from slugkit.base import StatsItem

stats = client.series.stats()
for item in stats:
    print(f"Event: {item.event_type}")
    print(f"Total Count: {item.total_count}")
    print(f"Request Count: {item.request_count}")
    print(f"Average Duration: {item.avg_duration_us}μs")
```

### SeriesInfo

Represents series information:

```python
from slugkit.base import SeriesInfo

series_info = client.series.info()
print(f"Pattern: {series_info.pattern}")
print(f"Capacity: {series_info.capacity}")
print(f"Generated: {series_info.generated_count}")
print(f"Last Modified: {series_info.mtime}")
```

### PatternInfo

Represents pattern information:

```python
from slugkit.base import PatternInfo

pattern_info = client.forge.pattern_info("test-{adjective}-{noun}")
print(f"Pattern: {pattern_info.pattern}")
print(f"Capacity: {pattern_info.capacity}")
print(f"Max Slug Length: {pattern_info.max_slug_length}")
print(f"Complexity: {pattern_info.complexity}")
print(f"Components: {pattern_info.components}")
```

### DictionaryInfo

Represents dictionary information:

```python
from slugkit.base import DictionaryInfo

dict_info = client.forge.dictionary_info()
for item in dict_info:
    print(f"Kind: {item.kind}, Count: {item.count}")
```

### DictionaryTag

Represents dictionary tags:

```python
from slugkit.base import DictionaryTag

dict_tags = client.forge.dictionary_tags()
for tag in dict_tags:
    print(f"Kind: {tag.kind}, Tag: {tag.tag}, Words: {tag.word_count}")
```

### SubscriptionFeatures

Represents subscription limits and features:

```python
from slugkit.base import SubscriptionFeatures

limits = client.limits()
print(f"Max Series: {limits.max_series}")
print(f"Requests Per Minute: {limits.req_per_minute}")
print(f"Forge Enabled: {limits.forge_enabled}")
print(f"Max Mint Per Day: {limits.max_mint_per_day}")
print(f"Max Mint Per Month: {limits.max_mint_per_month}")

# All fields are optional - None means not available
if limits.max_forge_per_request is not None:
    print(f"Max Forge Per Request: {limits.max_forge_per_request}")
```

## API Response Examples

### Stats Response

```json
[
  {
    "event_type": "mint",
    "date_part": "total",
    "total_count": 104517,
    "request_count": 118,
    "total_duration_us": 1092348,
    "avg_duration_us": 10.45
  },
  {
    "event_type": "forge",
    "date_part": "total",
    "total_count": 15,
    "request_count": 5,
    "total_duration_us": 500,
    "avg_duration_us": 50.0
  }
]
```

### Series Info Response

```json
{
  "slug": "whole-blond-rower-a597",
  "org_slug": "alias-first-glute-67d9",
  "pattern": "{adverb}-{adjective}-{noun}-{number:3d}",
  "max_pattern_length": 80,
  "capacity": "1281739952493000",
  "generated_count": "105",
  "mtime": "2025-08-29T00:54:35.128902+00:00"
}
```

### Pattern Info Response

```json
{
  "pattern": "{adjective}-{noun}-{number:3d}",
  "capacity": "1000000",
  "max_slug_length": 25,
  "complexity": 3,
  "components": 3
}
```

### Dictionary Info Response

```json
[
  {
    "kind": "adjective",
    "count": 1000
  },
  {
    "kind": "noun",
    "count": 2000
  },
  {
    "kind": "verb",
    "count": 1500
  }
]
```

### Dictionary Tags Response

```json
[
  {
    "kind": "adjective",
    "tag": "positive",
    "description": "Positive adjectives",
    "opt_in": true,
    "word_count": 500
  },
  {
    "kind": "noun",
    "tag": "animals",
    "description": "Animal names",
    "opt_in": false,
    "word_count": 300
  }
]
```

### Series List Response

```json
[
  "series-1",
  "series-2",
  "series-3"
]
```

## Error Handling

The SDK provides comprehensive error handling with custom exception types:

```python
from slugkit import SyncClient
from slugkit.base import (
    SlugKitConnectionError,
    SlugKitAuthenticationError,
    SlugKitValidationError,
    SlugKitRateLimitError,
    SlugKitQuotaError,
    SlugKitServerError,
)

client = SyncClient(
    base_url="https://dev.slugkit.dev/api/v1",
    api_key="your-api-key"
)

try:
    ids = client.series.mint(count=10)
except SlugKitRateLimitError as e:
    # Rate limiting with detailed information
    print(f"Rate limited: {e}")
    if e.rate_limit_reason:
        print(f"Reason: {e.rate_limit_reason}")
    if e.retry_after:
        print(f"Retry after: {e.retry_after} seconds")
    if e.rpm_remaining is not None:
        print(f"RPM remaining: {e.rpm_remaining}")
    if e.daily_remaining is not None:
        print(f"Daily remaining: {e.daily_remaining}")
except SlugKitAuthenticationError as e:
    print(f"Authentication failed: {e}")
except SlugKitValidationError as e:
    print(f"Validation error: {e}")
except SlugKitQuotaError as e:
    print(f"Quota exceeded: {e}")
except SlugKitConnectionError as e:
    print(f"Connection failed: {e}")
except SlugKitServerError as e:
    print(f"Server error: {e}")
```

### Rate Limiting

The SDK implements intelligent rate limit handling:

- **Automatic Retry**: Rate limit errors with `rate-limit-exceeded` or `daily-limit-exceeded` are automatically retried
- **Exponential Backoff**: Retry delays increase exponentially with jitter
- **Server Retry-After**: Respects `X-Slug-Retry-After` header from the server
- **Quota Visibility**: Shows remaining RPM, daily, monthly, and lifetime quotas
- **Smart Non-Retry**: Permanent failures (`not-available`, `request-size-exceeded`) and long-term limits (`monthly-limit-exceeded`, `lifetime-limit-exceeded`) are not retried

Rate limit reasons returned by the server:
- `rate-limit-exceeded` - RPM limit reached (retryable with accurate retry-after)
- `daily-limit-exceeded` - Daily limit reached (retryable with accurate retry-after)
- `monthly-limit-exceeded` - Monthly quota exceeded (non-retryable, wait until next month)
- `lifetime-limit-exceeded` - Lifetime quota exceeded (non-retryable, upgrade required)
- `request-size-exceeded` - Request size too large (non-retryable, reduce batch size)
- `not-available` - Feature not available to user (non-retryable, check subscription)
- `redis-error` - Server error (non-retryable, contact support)

## Pattern Language

The SDK supports SlugKit's pattern language for generating structured IDs:

### Basic Tokens

- `{adjective}` - Random adjective
- `{noun}` - Random noun  
- `{adverb}` - Random adverb
- `{verb}` - Random verb

### Number Generators

- `{number:3d}` - 3-digit decimal number
- `{number:4,hex}` - 4-character hexadecimal
- `{number:2r}` - up to 2-character roman number, lowercase
- `{number:6R}` - up to 6-character roman number, uppercase

### Examples

```python
# Simple patterns
pattern1 = "{adjective}-{noun}"
pattern2 = "{color}-{animal}-{number:3d}"

# Complex patterns with constraints
pattern3 = "{adverb}-{adjective}-{noun}-{number:4,hex}[==5]"

# Generate IDs
ids = client.forge(pattern=pattern3, count=5)
```

## MCP Server: AI Assistant Integration

**⚡ The SlugKit MCP Server enables AI assistants to generate truly unique identifiers!**

### The Problem with AI-Generated IDs

AI assistants cannot generate truly unique strings because they:
- Have no persistence between conversations
- Cannot coordinate across multiple instances
- Generate probabilistic, not truly random content
- Have no concept of sequential uniqueness

This makes AI-generated identifiers unsuitable for production use where uniqueness is critical.

### The Solution: SlugKit MCP Integration

The SlugKit MCP (Model Context Protocol) server connects AI assistants like Claude Desktop, Cursor, and Warp directly to SlugKit's guaranteed-unique ID generation service.

**Key Benefits:**
- ✅ **Guaranteed Uniqueness** - Mathematical guarantees, not probabilistic generation
- ✅ **Sequential Consistency** - Proper sequential IDs across all sessions
- ✅ **Production Ready** - Battle-tested for high-volume applications
- ✅ **Zero Collisions** - Impossible to generate duplicate IDs
- ✅ **Pattern Flexibility** - Generate IDs matching your exact requirements

### Quick Setup

**Cloud Instance (Recommended):**
```json
{
    "mcpServers": {
        "SlugKit": {
            "command": "npx",
            "args": [
                "-y", "mcp-remote",
                "https://dev.slugkit.dev/api/v1/mcp",
                "--header", "x-api-key:YOUR_API_KEY_HERE"
            ]
        }
    }
}
```

**Local Installation:**
```bash
pip install slugkit-py-sdk
```

```json
{
    "mcpServers": {
        "SlugKit": {
            "command": "slugkit-mcp",
            "env": {
                "SLUGKIT_API_KEY": "YOUR_API_KEY_HERE"
            }
        }
    }
}
```

### Usage Examples

Once configured, ask your AI assistant:

```
"Generate 10 unique user IDs with the pattern user-{adjective}-{noun}-{number:4d}"
```
*→ Returns guaranteed-unique IDs like "user-happy-dolphin-0001", "user-bright-falcon-0002"*

```
"Analyze this pattern: {color}-{animal}-{number:3,hex} - how many unique IDs can it generate?"
```
*→ Shows capacity analysis: "1.2M unique combinations, medium complexity"*

```
"Compare these URL slug patterns and recommend the best one: {adjective}-{noun} vs {verb}-{noun}-{number:2d}"
```
*→ Generates samples, analyzes capacity, recommends optimal choice*

### Available Capabilities

The MCP server provides AI assistants with access to:

- **ID Generation:** `forge` (custom patterns), `mint` (series), `slice` (preview)
- **Pattern Analysis:** `validate_pattern`, `analyze_pattern`, `compare_patterns` 
- **Information:** `dictionary_info`, `series_info`, `key_info`, `stats`
- **Management:** `series_list`, `reset` (dev/test)
- **Documentation:** `get_help_topic`, pattern syntax references

**📚 For detailed setup instructions, troubleshooting, and advanced configuration, see [README_MCP.md](README_MCP.md)**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
