# SlugKit Python SDK

A Python SDK for generating human-readable IDs using SlugKit.dev service.

Please see [SlugKit documentation](https://dev.slugkit.dev) for information
on creating projects and obtaining API keys.

## Installation

```bash
pip install slugkit-py-sdk
```

## API Overview

The SDK provides a simple interface to generate human-readable IDs and test patterns.

### Basic Usage

```python
from slugkit import SyncClient

# Initialize the client
client = SyncClient(
    base_url="https://dev.slugkit.dev/api/v1",
    api_key="your-api-key"
)

# Generate a single ID
id = client.generator()[0]

# Generate multiple IDs
ids = client.generator(count=5)

# Get generator stats
stats = client.generator.stats()

# Reset the generator
client.generator.reset()
```

### Pattern Testing

```python
from slugkit import PatternTester
import httpx

# Initialize the tester
client = slugkit.SyncClient(base_url="https://dev.slugkit.dev/api/v1")

# Test a pattern
ids = client.test(
    pattern="your-pattern",
    seed="optional-seed",
    sequence=1,
    count=5
)
```

## Command Line Interface

The SDK includes a command-line interface for easy usage:

### Generate IDs

```bash
# Generate a single ID
slugkit next

# Generate multiple IDs
slugkit next 5

# Generate IDs with custom batch size
slugkit next 10 --batch-size 2
```

### Test Patterns

```bash
# Test a pattern
slugkit pattern-test "your-pattern"

# Test with specific seed and sequence
slugkit pattern-test "your-pattern" --seed "my-seed" --sequence 1

# Generate multiple test IDs
slugkit pattern-test "your-pattern" --count 5
```

### Generator Management

```bash
# Get generator stats
slugkit stats

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
slugkit --base-url "https://dev.slugkit.dev/api/v1" --api-key "your-api-key" next
```

### Output Format

The CLI supports different output formats:

```bash
# Text output (default)
slugkit next

# JSON output
slugkit next --output-format json
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
