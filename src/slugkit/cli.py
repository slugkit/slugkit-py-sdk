import time
import typer
import dotenv
import httpx
import json
import logging
import uuid

from enum import Enum

from slugkit import SyncClient
from slugkit.sync_client import RandomGenerator
from slugkit.base import StatsItem, SeriesInfo, SubscriptionFeatures, DEFAULT_BATCH_SIZE
from slugkit.package_data import list_package_files, get_package_data
from slugkit.errors import SlugKitError

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


def print_series_info(series_info: SeriesInfo):
    caption_width = 25
    print(f"{'Series Slug':<{caption_width}}: {series_info.slug}")
    print(f"{'Organization Slug':<{caption_width}}: {series_info.org_slug}")
    print(f"{'Name':<{caption_width}}: {series_info.name}")
    print(f"{'Pattern':<{caption_width}}: {series_info.pattern}")
    print(f"{'Max Slug Length':<{caption_width}}: {series_info.max_slug_length}")
    print(f"{'Capacity':<{caption_width}}: {series_info.capacity}")
    print(f"{'Generated Count':<{caption_width}}: {series_info.generated_count}")
    print(f"{'Last Modified':<{caption_width}}: {series_info.mtime}")


@app.callback()
def callback(
    *,
    base_url: str = typer.Option(
        ...,  # "https://dev.slugkit.dev/api/v1",
        envvar="SLUGKIT_BASE_URL",
        help="The base URL of the SlugKit API.",
    ),
    api_key: str = typer.Option(
        ...,
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
def ping():
    """
    Ping the SlugKit API.
    """
    try:
        client = SyncClient(app_context.base_url, app_context.api_key)
        start_time = time.time()
        client.ping()
        end_time = time.time()
        logger.info(f"Ping successful in {end_time - start_time:.2f} seconds")
    except SlugKitError as e:
        logger.error(f"Failed to ping: {e}")
        raise typer.Exit(1)


@app.command()
def key_info():
    """
    Get information about the current key.
    """
    client = SyncClient(app_context.base_url, app_context.api_key)
    try:
        key_info = client.key_info()
        if app_context.output_format == OutputFormat.JSON:
            print(json.dumps(key_info.to_dict(), indent=2))
        else:
            caption_width = 25
            print(f"{'Type':<{caption_width}}: {key_info.type}")
            print(f"{'Key Scope':<{caption_width}}: {key_info.key_scope.value}")
            print(f"{'Slug':<{caption_width}}: {key_info.slug}")
            print(f"{'Org Slug':<{caption_width}}: {key_info.org_slug}")
            print(f"{'Series Slug':<{caption_width}}: {key_info.series_slug}")
            print(f"{'Scopes':<{caption_width}}: {key_info.scopes}")
            print(f"{'Enabled':<{caption_width}}: {key_info.enabled}")
    except SlugKitError as e:
        logger.error(f"Failed to get key info: {e.response.text}")
        raise typer.Exit(1)


@app.command()
def limits():
    """
    Get subscription limits and features for the organisation.
    """
    client = SyncClient(app_context.base_url, app_context.api_key)
    try:
        limits = client.limits()
        if app_context.output_format == OutputFormat.JSON:
            print(json.dumps(limits.to_dict(), indent=2))
        else:
            caption_width = 30

            def fmt(value):
                """Format value, showing 'N/A' for None."""
                return value if value is not None else 'N/A'

            print("=== Series Limits ===")
            print(f"{'Max Series':<{caption_width}}: {fmt(limits.max_series)}")
            print()
            print("=== Rate Limits ===")
            print(f"{'Requests Per Minute':<{caption_width}}: {fmt(limits.req_per_minute)}")
            print(f"{'Burst Requests Per Minute':<{caption_width}}: {fmt(limits.burst_req_per_minute)}")
            print()
            print("=== Forge Limits ===")
            print(f"{'Forge Enabled':<{caption_width}}: {fmt(limits.forge_enabled)}")
            print(f"{'Max Forge Per Day':<{caption_width}}: {fmt(limits.max_forge_per_day)}")
            print(f"{'Max Forge Per Month':<{caption_width}}: {fmt(limits.max_forge_per_month)}")
            print(f"{'Max Forge Per Request':<{caption_width}}: {fmt(limits.max_forge_per_request)}")
            print()
            print("=== Mint Limits ===")
            print(f"{'Mint Enabled':<{caption_width}}: {fmt(limits.mint_enabled)}")
            print(f"{'Max Mint Per Day':<{caption_width}}: {fmt(limits.max_mint_per_day)}")
            print(f"{'Max Mint Per Month':<{caption_width}}: {fmt(limits.max_mint_per_month)}")
            print(f"{'Max Mint Per Request':<{caption_width}}: {fmt(limits.max_mint_per_request)}")
            print()
            print("=== Slice Limits ===")
            print(f"{'Slice Enabled':<{caption_width}}: {fmt(limits.slice_enabled)}")
            print(f"{'Slice Window Back':<{caption_width}}: {fmt(limits.slice_window_back)}")
            print(f"{'Slice Window Forward':<{caption_width}}: {fmt(limits.slice_window_forward)}")
            print()
            print("=== Access Control ===")
            print(f"{'API Key Access':<{caption_width}}: {fmt(limits.api_key_access)}")
            print(f"{'API Key Scopes':<{caption_width}}: {', '.join(limits.api_key_scopes) if limits.api_key_scopes else 'N/A'}")
            print(f"{'SDK Access':<{caption_width}}: {fmt(limits.sdk_access)}")
            print(f"{'SDK Scopes':<{caption_width}}: {', '.join(limits.sdk_scopes) if limits.sdk_scopes else 'N/A'}")
            print()
            print("=== Other ===")
            print(f"{'Max Nodes':<{caption_width}}: {fmt(limits.max_nodes)}")
            print(f"{'Custom Features':<{caption_width}}: {fmt(limits.custom_features)}")
    except SlugKitError as e:
        logger.error(f"Failed to get limits: {e}")
        raise typer.Exit(1)


@app.command()
def pattern_info(
    pattern: str = typer.Argument(..., help="The pattern to get information about."),
):
    """
    Get information about a pattern.
    """
    client = SyncClient(app_context.base_url, app_context.api_key)
    try:
        pattern_info = client.forge.pattern_info(pattern)
        if app_context.output_format == OutputFormat.JSON:
            print(json.dumps(pattern_info.to_dict(), indent=2))
        else:
            caption_width = 25
            print(f"{'Pattern':<{caption_width}}: {pattern_info.pattern}")
            print(f"{'Capacity':<{caption_width}}: {pattern_info.capacity}")
            print(f"{'Max Slug Length':<{caption_width}}: {pattern_info.max_slug_length}")
            print(f"{'Complexity':<{caption_width}}: {pattern_info.complexity}")
            print(f"{'Components':<{caption_width}}: {pattern_info.components}")
    except SlugKitError as e:
        logger.error(f"Failed to get pattern info: {e}")
        raise typer.Exit(1)


@app.command()
def forge(
    pattern: str = typer.Argument(..., help="The slug pattern to test."),
    *,
    seed: str | None = typer.Option(None, "--seed", "-s", help="The seed to use for the random number generator."),
    sequence: int | None = typer.Option(
        None, "--sequence", "-n", help="The sequence number to use for the random number generator."
    ),
    count: int = typer.Option(1, "--count", "-c", help="The number of human-readable IDs to generate."),
):
    """
    Get a list of slugs for a given pattern.
    """
    if seed is None:
        seed = str(uuid.uuid4())
    client = SyncClient(app_context.base_url, app_context.api_key)
    try:
        result = client.forge(pattern, seed=seed, sequence=sequence, count=count)
    except SlugKitError as e:
        logger.error(f"Failed to test pattern: {e}")
        raise typer.Exit(1)
    if app_context.output_format == OutputFormat.JSON:
        print(json.dumps(result, indent=2))
    else:
        for slug in result:
            print(slug)


@app.command()
def mint(
    count: int = typer.Argument(1, help="The number of slugs to generate."),
    batch_size: int = typer.Option(DEFAULT_BATCH_SIZE, "--batch-size", "-b", help="Size of a batch to fetch at once."),
    series: str | None = typer.Option(None, "--series", "-s", help="The series to use for the slugs."),
):
    """
    Generate next batch of slugs for the series defined by the API key.

    Generating slugs will bump the series counter. Slugs may be generated
    concurrently and will not collide.

    If the output format is JSON, the result will be a list of slugs.
    Otherwise, the result will be a stream of slugs.
    Default output format is text.
    """
    logger.info(f"Generating {count} human-readable IDs at {app_context.base_url}")
    client = SyncClient(app_context.base_url, app_context.api_key)
    if series:
        client = client.series[series]
    else:
        client = client.series
    gen = client.mint
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
def slice(
    sequence: int = typer.Argument(0, help="The sequence number to start from."),
    count: int = typer.Argument(1, help="The number of slugs to generate."),
    batch_size: int = typer.Option(DEFAULT_BATCH_SIZE, "--batch-size", "-b", help="Size of a batch to fetch at once."),
    series: str | None = typer.Option(None, "--series", "-s", help="The series to use for the slugs."),
):
    """
    Generate slugs starting from a given sequence number.
    Series counters are not bumped.
    """
    client = SyncClient(app_context.base_url, app_context.api_key)
    if series:
        client = client.series[series]
    else:
        client = client.series
    gen = client.slice.starting_from(sequence)
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
def stats(
    series: str | None = typer.Option(None, "--series", "-s", help="The series to use for the stats."),
):
    """
    Get the stats of the generator.
    """
    client = SyncClient(app_context.base_url, app_context.api_key)
    if series:
        client = client.series[series]
    else:
        client = client.series
    try:
        stats_items = client.stats()
        if app_context.output_format == OutputFormat.JSON:
            # Convert StatsItem objects to dictionaries for JSON serialization
            stats_dicts = [item.to_dict() for item in stats_items]
            print(json.dumps(stats_dicts, indent=2))
        else:
            caption_width = 25
            for item in stats_items:
                print(f"{'Event Type':<{caption_width}}: {item.event_type}")
                print(f"{'Date Part':<{caption_width}}: {item.date_part}")
                print(f"{'Total Count':<{caption_width}}: {item.total_count}")
                print(f"{'Request Count':<{caption_width}}: {item.request_count}")
                print(f"{'Total Duration (μs)':<{caption_width}}: {item.total_duration_us}")
                print(f"{'Avg Duration (μs)':<{caption_width}}: {item.avg_duration_us}")
                print("-" * 50)
    except SlugKitError as e:
        logger.error(f"Failed to get stats: {e}")
        raise typer.Exit(1)


@app.command()
def series_info(
    series: str | None = typer.Option(None, "--series", "-s", help="The series to use for the info."),
):
    """
    Get information about the current series.
    """
    client = SyncClient(app_context.base_url, app_context.api_key)
    if series:
        client = client.series[series]
    else:
        client = client.series
    try:
        series_info = client.info()
        if app_context.output_format == OutputFormat.JSON:
            # Convert SeriesInfo object to dictionary for JSON serialization
            series_dict = series_info.to_dict()
            print(json.dumps(series_dict, indent=2))
        else:
            print_series_info(series_info)
    except SlugKitError as e:
        logger.error(f"Failed to get series info: {e}")
        raise typer.Exit(1)


@app.command()
def list_series():
    """
    Get the list of available series.
    """
    client = SyncClient(app_context.base_url, app_context.api_key)
    try:
        series_list = client.series.list()
        if app_context.output_format == OutputFormat.JSON:
            print(json.dumps(series_list, indent=2))
        else:
            print("Series:")
            if isinstance(series_list, list):
                for series in series_list:
                    print(series)
            elif isinstance(series_list, dict):
                caption_width = 25
                for key, name in series_list.items():
                    print(f"{key:<{caption_width}}: {name}")
            else:
                print(series_list)
    except SlugKitError as e:
        logger.error(f"Failed to get series list: {e}")
        raise typer.Exit(1)


@app.command()
def create_series(
    name: str = typer.Argument(..., help="The name of the series."),
    pattern: str = typer.Argument(..., help="The pattern of the series."),
):
    """
    Create a new series.
    """
    client = SyncClient(app_context.base_url, app_context.api_key)
    try:
        series_info = client.series.create(name, pattern)
        if app_context.output_format == OutputFormat.JSON:
            print(json.dumps(series_info.to_dict(), indent=2))
        else:
            print_series_info(series_info)
    except SlugKitError as e:
        logger.error(f"Failed to create series: {e}")
        raise typer.Exit(1)


@app.command()
def update_series(
    series: str | None = typer.Option(None, "--series", "-s", help="The series to use for the info."),
    name: str = typer.Argument(..., help="The name of the series."),
    pattern: str = typer.Argument(..., help="The pattern of the series."),
):
    """
    Update a series.
    """
    client = SyncClient(app_context.base_url, app_context.api_key)
    if series:
        client = client.series[series]
    else:
        client = client.series
    try:
        series_info = client.update(name, pattern)
        if app_context.output_format == OutputFormat.JSON:
            print(json.dumps(series_info.to_dict(), indent=2))
        else:
            print_series_info(series_info)
    except SlugKitError as e:
        logger.error(f"Failed to update series: {e}")
        raise typer.Exit(1)


@app.command()
def delete_series(
    series: str = typer.Option(..., "--series", "-s", help="The series to use for the info."),
):
    """
    Delete a series.
    """
    client = SyncClient(app_context.base_url, app_context.api_key).series[series]
    try:
        client.delete()
        logger.info(f"Series {series} deleted")
    except SlugKitError as e:
        logger.error(f"Failed to delete series: {e}")
        raise typer.Exit(1)


@app.command()
def reset(
    series: str | None = typer.Option(None, "--series", "-s", help="The series to use for the reset."),
):
    """
    Reset the generator.
    """
    try:
        logger.warning(f"Resetting generator at {app_context.base_url}")
        client = SyncClient(app_context.base_url, app_context.api_key)
        if series:
            client = client.series[series]
        else:
            client = client.series
        client.reset()
        logger.info("Generator reset")
    except SlugKitError as e:
        logger.error(f"Failed to reset generator: {e}")
        raise typer.Exit(1)


@app.command()
def validate(pattern: str):
    """
    Get information about a pattern.
    """
    client = SyncClient(app_context.base_url, app_context.api_key)
    try:
        pattern_info = client.forge.pattern_info(pattern)
        if app_context.output_format == OutputFormat.JSON:
            print(json.dumps(pattern_info.to_dict(), indent=2))
        else:
            caption_width = 25
            print(f"{'Pattern':<{caption_width}}: {pattern_info.pattern}")
            print(f"{'Capacity':<{caption_width}}: {pattern_info.capacity}")
            print(f"{'Max Slug Length':<{caption_width}}: {pattern_info.max_slug_length}")
            print(f"{'Complexity':<{caption_width}}: {pattern_info.complexity}")
            print(f"{'Components':<{caption_width}}: {pattern_info.components}")
    except SlugKitError as e:
        logger.error(f"Failed to validate pattern: {e}")
        raise typer.Exit(1)


@app.command()
def docs():
    """
    Get package documentation.
    """
    for file in list_package_files():
        print(file)


@app.command()
def doc(file: str):
    """
    Get package documentation.
    """
    print(get_package_data(file))


def main():
    dotenv.load_dotenv()
    app()


if __name__ == "__main__":
    main()
