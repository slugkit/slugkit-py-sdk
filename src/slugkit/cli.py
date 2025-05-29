import typer
import dotenv
import httpx
import json
import logging
import uuid

from enum import Enum

from slugkit import SyncClient
from slugkit.sync_client import PatternTester

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.ERROR)

app = typer.Typer()


class OutputFormat(str, Enum):
    JSON = "json"
    TEXT = "text"


class AppContext:
    base_url: str
    api_key: str
    output_format: OutputFormat = OutputFormat.TEXT

    allow_extra_args: bool = False
    allow_interspersed_args: bool = False

    ignore_unknown_options: bool = False

    def __init__(self, base_url: str, api_key: str, output_format: OutputFormat):
        self.base_url = base_url
        self.api_key = api_key
        self.output_format = output_format


app_context = typer.Context(AppContext)


@app.callback()
def callback(
    *,
    base_url: str = typer.Option(
        ...,  # "https://dev.slugkit.dev/api/v1",
        envvar="SLUGKIT_BASE_URL",
        help="The base URL of the SlugKit API.",
    ),
    api_key: str | None = typer.Option(
        None,
        envvar="SLUGKIT_API_KEY",
        help="The API key for the SlugKit API.",
    ),
    output_format: OutputFormat = typer.Option(
        OutputFormat.TEXT,
        "--output-format",
        "-o",
        help="The output format to use for the human-readable IDs.",
    ),
):
    """
    SlugKit Python SDK.
    """
    app_context.base_url = base_url
    app_context.api_key = api_key
    app_context.output_format = output_format


@app.command()
def pattern_test(
    pattern: str = typer.Argument(..., help="The slug pattern to test."),
    *,
    seed: str | None = typer.Option(None, "--seed", "-s", help="The seed to use for the random number generator."),
    sequence: int | None = typer.Option(
        None, "--sequence", "-n", help="The sequence number to use for the random number generator."
    ),
    count: int = typer.Option(1, "--count", "-c", help="The number of human-readable IDs to generate."),
):
    """
    Get a list of human-readable IDs for a given pattern.

    Args:
        pattern: The pattern to test.
        seed: The seed to use for the random number generator.
        sequense: The sequence number to use for the random number generator.
        count: The number of human-readable IDs to generate.
    """
    if seed is None:
        seed = str(uuid.uuid4())
    client = SyncClient(app_context.base_url, app_context.api_key)
    result = client.test(pattern, seed=seed, sequence=sequence, count=count)
    if app_context.output_format == OutputFormat.JSON:
        print(json.dumps(result, indent=2))
    else:
        for slug in result:
            print(slug)


@app.command()
def next(
    count: int = typer.Argument(1, help="The number of human-readable IDs to generate."),
    batch_size: int = typer.Option(
        10, "--batch-size", "-b", help="The number of human-readable IDs to generate in a batch."
    ),
):
    """
    Generate next batch of human-readable IDs for the project defined by
    the API key.

    If the output format is JSON, the result will be a list of human-readable IDs.
    Otherwise, the result will be a stream of human-readable IDs.
    Default output format is text.
    """
    logger.info(f"Generating {count} human-readable IDs at {app_context.base_url}")
    client = SyncClient(app_context.base_url, app_context.api_key)
    gen = client.generator
    if count > 1:
        gen = gen.with_limit(count).with_batch_size(batch_size)
        if app_context.output_format == OutputFormat.JSON:
            print(json.dumps(list(gen), indent=2))
        else:
            for slug in gen:
                print(slug)
    elif count == 1:
        if app_context.output_format == OutputFormat.JSON:
            print(json.dumps(gen(), indent=2))
        else:
            print(gen()[0])
    else:
        raise ValueError(f"Invalid count: {count}")


@app.command()
def stats():
    """
    Get the stats of the generator.
    """
    client = SyncClient(app_context.base_url, app_context.api_key)
    try:
        stats = client.generator.stats()
        if app_context.output_format == OutputFormat.JSON:
            print(json.dumps(stats, indent=2))
        else:
            caption_width = 20
            print(f"{'Project name':<{caption_width}}: {stats['name']}")
            print(f"{'Project slug':<{caption_width}}: {stats['slug']}")
            print(f"{'Pattern':<{caption_width}}: {stats['pattern']}")
            print(f"{'Capacity':<{caption_width}}: {stats['capacity']}")
            print(f"{'Generated IDs':<{caption_width}}: {stats['generated_ids_count']}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to get stats: {e.response.text}")
        raise typer.Exit(1)


@app.command()
def reset():
    """
    Reset the generator.
    """
    try:
        logger.warning(f"Resetting generator at {app_context.base_url}")
        client = SyncClient(app_context.base_url, app_context.api_key)
        client.generator.reset()
        logger.info("Generator reset")
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to reset generator: {e.response.text}")
        raise typer.Exit(1)


def main():
    dotenv.load_dotenv()
    app()


if __name__ == "__main__":
    main()
