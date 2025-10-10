"""Velithon CLI module providing command-line interface for the framework.

This module provides CLI commands for running the server and exporting documentation.
"""

import importlib
import pathlib
import sys
import traceback
from typing import Any

import click
import granian
import granian.http

from velithon.logging import get_logger

logger = get_logger(__name__)

project_root = pathlib.Path.cwd()  # Use current working directory
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))  # Insert at the beginning to prioritize


class ImportFromStringError(Exception):
    """Exception raised when import from string fails."""

    pass


def import_from_string(import_str: Any) -> Any:
    """Import and return an object from a module path string.

    Args:
        import_str: String in format "module:attribute"

    Returns:
        The imported object

    Raises:
        ImportFromStringError: If import fails

    """
    if not isinstance(import_str, str):
        return import_str

    module_str, _, attrs_str = import_str.partition(':')
    if not module_str or not attrs_str:
        message = (
            'Import string "{import_str}" must be in format "<module>:<attribute>".'
        )
        raise ImportFromStringError(message.format(import_str=import_str))

    try:
        module = importlib.import_module(module_str)
    except ModuleNotFoundError as exc:
        if exc.name != module_str:
            raise exc from None
        message = 'Could not import module "{module_str}".'
        raise ImportFromStringError(message.format(module_str=module_str)) from None

    instance = module
    try:
        for attr_str in attrs_str.split('.'):
            instance = getattr(instance, attr_str)
    except AttributeError:
        message = 'Attribute "{attrs_str}" not found in module "{module_str}".'
        raise ImportFromStringError(
            message.format(attrs_str=attrs_str, module_str=module_str)
        ) from None

    return instance


@click.group()
def cli() -> None:
    """Velithon CLI - A lightweight RSGI-based web framework."""
    pass


@cli.command()
@click.option(
    '--app',
    default='simple_app:app',
    help='Application module and instance (format: module:app_instance).',
)
@click.option('--host', default='127.0.0.1', help='Host to bind.')
@click.option('--port', default=8000, type=int, help='Port to bind.')
@click.option('--workers', default=1, type=int, help='Number of worker processes.')
@click.option('--log-file', default='velithon.log', help='Log file path.')
@click.option(
    '--log-level',
    default='INFO',
    type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']),
    help='Logging level.',
)
@click.option(
    '--log-format',
    default='text',
    type=click.Choice(['text', 'json']),
    help='Log format.',
)
@click.option('--log-to-file', is_flag=True, help='Enable logging to file.')
@click.option(
    '--max-bytes',
    default=10 * 1024 * 1024,
    type=int,
    help='Max bytes for log file rotation.',
)
@click.option(
    '--backup-count', default=7, type=int, help='Number of backup log files. (days)'
)
@click.option(
    '--blocking-threads', default=None, type=int, help='Number of blocking threads.'
)
@click.option(
    '--blocking-threads-idle-timeout',
    default=30,
    type=int,
    help='Idle timeout for blocking threads.',
)
@click.option(
    '--runtime-threads', default=1, type=int, help='Number of runtime threads.'
)
@click.option(
    '--runtime-blocking-threads',
    default=None,
    type=int,
    help='Number of blocking threads for runtime.',
)
@click.option(
    '--runtime-mode',
    default='st',
    type=click.Choice(['st', 'mt']),
    help='Runtime mode (single-threaded or multi-threaded).',
)
@click.option(
    '--loop',
    default='auto',
    type=click.Choice(['auto', 'asyncio', 'uvloop', 'rloop']),
    help='Event loop to use.',
)
@click.option(
    '--task-impl',
    default='asyncio',
    type=click.Choice(['asyncio', 'rust']),
    help='Task implementation to use. **Note**: `rust` is only support in python <= 3.12',  # noqa: E501
)
@click.option(
    '--http',
    default='auto',
    type=click.Choice(['auto', '1', '2']),
    help='HTTP mode to use.',
)
@click.option(
    '--http1-buffer-size',
    type=click.IntRange(8192),
    default=granian.http.HTTP1Settings.max_buffer_size,
    help='Sets the maximum buffer size for HTTP/1 connections',
)
@click.option(
    '--http1-header-read-timeout',
    type=click.IntRange(1, 60_000),
    default=granian.http.HTTP1Settings.header_read_timeout,
    help='Sets a timeout (in milliseconds) to read headers',
)
@click.option(
    '--http1-keep-alive/--no-http1-keep-alive',
    default=granian.http.HTTP1Settings.keep_alive,
    help='Enables or disables HTTP/1 keep-alive',
)
@click.option(
    '--http1-pipeline-flush/--no-http1-pipeline-flush',
    default=granian.http.HTTP1Settings.pipeline_flush,
    help='Aggregates HTTP/1 flushes to better support pipelined responses (experimental)',  # noqa: E501
)
@click.option(
    '--http2-adaptive-window/--no-http2-adaptive-window',
    default=granian.http.HTTP2Settings.adaptive_window,
    help='Sets whether to use an adaptive flow control for HTTP2',
)
@click.option(
    '--http2-initial-connection-window-size',
    type=click.IntRange(1024),
    default=granian.http.HTTP2Settings.initial_connection_window_size,
    help='Sets the max connection-level flow control for HTTP2',
)
@click.option(
    '--http2-initial-stream-window-size',
    type=click.IntRange(1024),
    default=granian.http.HTTP2Settings.initial_stream_window_size,
    help='Sets the `SETTINGS_INITIAL_WINDOW_SIZE` option for HTTP2 stream-level flow control',  # noqa: E501
)
@click.option(
    '--http2-keep-alive-interval',
    type=click.IntRange(1, 60_000),
    default=granian.http.HTTP2Settings.keep_alive_interval,
    help='Sets an interval (in milliseconds) for HTTP2 Ping frames should be sent to keep a connection alive',  # noqa: E501
)
@click.option(
    '--http2-keep-alive-timeout',
    type=click.IntRange(1),
    default=granian.http.HTTP2Settings.keep_alive_timeout,
    help='Sets a timeout (in seconds) for receiving an acknowledgement of the HTTP2 keep-alive ping',  # noqa: E501
)
@click.option(
    '--http2-max-concurrent-streams',
    type=click.IntRange(10),
    default=granian.http.HTTP2Settings.max_concurrent_streams,
    help='Sets the SETTINGS_MAX_CONCURRENT_STREAMS option for HTTP2 connections',
)
@click.option(
    '--http2-max-frame-size',
    type=click.IntRange(1024),
    default=granian.http.HTTP2Settings.max_frame_size,
    help='Sets the maximum frame size to use for HTTP2',
)
@click.option(
    '--http2-max-headers-size',
    type=click.IntRange(1),
    default=granian.http.HTTP2Settings.max_headers_size,
    help='Sets the max size of received header frames',
)
@click.option(
    '--http2-max-send-buffer-size',
    type=click.IntRange(1024),
    default=granian.http.HTTP2Settings.max_send_buffer_size,
    help='Set the maximum write buffer size for each HTTP/2 stream',
)
@click.option(
    '--ssl-certificate',
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        path_type=pathlib.Path,
    ),
    help='SSL certificate file',
)
@click.option(
    '--ssl-keyfile',
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        path_type=pathlib.Path,
    ),
    help='SSL key file',
)
@click.option('--ssl-keyfile-password', help='SSL key password')
@click.option(
    '--backpressure',
    default=None,
    type=int,
    help=' Maximum number of requests to process concurrently (per worker)',
)
@click.option('--reload', is_flag=True, help='Enable auto-reload for development.')
def run(
    app,
    host,
    port,
    workers,
    log_file,
    log_level,
    log_format,
    log_to_file,
    max_bytes,
    backup_count,
    reload,
    blocking_threads,
    blocking_threads_idle_timeout,
    runtime_threads,
    runtime_blocking_threads,
    runtime_mode,
    loop,
    task_impl,
    http,
    http1_buffer_size,
    http1_header_read_timeout,
    http1_keep_alive,
    http1_pipeline_flush,
    http2_adaptive_window,
    http2_initial_connection_window_size,
    http2_initial_stream_window_size,
    http2_keep_alive_interval,
    http2_keep_alive_timeout,
    http2_max_concurrent_streams,
    http2_max_frame_size,
    http2_max_headers_size,
    http2_max_send_buffer_size,
    ssl_certificate,
    ssl_keyfile,
    ssl_keyfile_password,
    backpressure,
):
    """Run the Velithon application."""
    try:
        app_instance = import_from_string(app)
        if not callable(app_instance):
            raise ImportFromStringError(
                f"'{app}' is not a callable application instance."
            )
        app_instance._serve(
            app,
            host,
            port,
            workers,
            log_file,
            log_level,
            log_format,
            log_to_file,
            max_bytes,
            backup_count,
            reload,
            blocking_threads,
            blocking_threads_idle_timeout,
            runtime_threads,
            runtime_blocking_threads,
            runtime_mode,
            loop,
            task_impl,
            http,
            http1_buffer_size,
            http1_header_read_timeout,
            http1_keep_alive,
            http1_pipeline_flush,
            http2_adaptive_window,
            http2_initial_connection_window_size,
            http2_initial_stream_window_size,
            http2_keep_alive_interval,
            http2_keep_alive_timeout,
            http2_max_concurrent_streams,
            http2_max_frame_size,
            http2_max_headers_size,
            http2_max_send_buffer_size,
            ssl_certificate,
            ssl_keyfile,
            ssl_keyfile_password,
            backpressure,
        )

    except ValueError as e:
        traceback.print_exc()
        logger.error(f'Error: {e!s}')
    except Exception as e:
        traceback.print_exc()
        logger.error(f'Failed to start server: {e!s}')


@cli.command()
@click.option(
    '--app',
    default='simple_app:app',
    help='Application module and instance (format: module:app_instance).',
)
@click.option(
    '--output',
    default='api_docs',
    help='Output file path (without extension).',
)
@click.option(
    '--format',
    'output_format',
    default='markdown',
    type=click.Choice(['markdown', 'pdf', 'both']),
    help='Output format.',
)
@click.option(
    '--title',
    default='API Documentation',
    help='Documentation title.',
)
@click.option(
    '--version',
    default='1.0.0',
    help='API version.',
)
@click.option(
    '--description',
    default='Generated API Documentation',
    help='API description.',
)
@click.option(
    '--contact-name',
    default='',
    help='Contact name.',
)
@click.option(
    '--contact-email',
    default='',
    help='Contact email.',
)
@click.option(
    '--license-name',
    default='',
    help='License name.',
)
@click.option(
    '--license-url',
    default='',
    help='License URL.',
)
@click.option(
    '--exclude-routes',
    help='Comma-separated list of route paths/names to exclude.',
)
@click.option(
    '--include-only-routes',
    help='Comma-separated list of route paths/names to include (excludes all others).',
)
@click.option(
    '--group-by-tags/--no-group-by-tags',
    default=True,
    help='Group routes by tags.',
)
@click.option(
    '--include-examples/--no-include-examples',
    default=True,
    help='Include examples in documentation.',
)
@click.option(
    '--include-schemas/--no-include-schemas',
    default=True,
    help='Include schemas in documentation.',
)
def export_docs(
    app,
    output,
    output_format,
    title,
    version,
    description,
    contact_name,
    contact_email,
    license_name,
    license_url,
    exclude_routes,
    include_only_routes,
    group_by_tags,
    include_examples,
    include_schemas,
):
    """Export comprehensive API documentation."""
    try:
        from velithon.documentation import DocumentationConfig, DocumentationGenerator

        # Import the application
        app_instance = import_from_string(app)
        if not hasattr(app_instance, 'router'):
            raise ImportFromStringError(
                f"'{app}' is not a valid Velithon application instance."
            )

        # Parse exclude/include routes
        exclude_list = []
        if exclude_routes:
            exclude_list = [route.strip() for route in exclude_routes.split(',')]

        include_only_list = None
        if include_only_routes:
            include_only_list = [
                route.strip() for route in include_only_routes.split(',')
            ]

        # Create documentation config
        config = DocumentationConfig(
            title=title,
            version=version,
            description=description,
            contact_name=contact_name,
            contact_email=contact_email,
            license_name=license_name,
            license_url=license_url,
            exclude_routes=exclude_list,
            include_only_routes=include_only_list,
            group_by_tags=group_by_tags,
            include_examples=include_examples,
            include_schemas=include_schemas,
        )

        # Generate documentation
        generator = DocumentationGenerator(app_instance, config)
        routes_info = generator.collect_routes_info()

        if not routes_info:
            click.echo('No routes found to document.', err=True)
            return

        click.echo(f'Found {len(routes_info)} routes to document.')

        # Export based on format
        if output_format in ('markdown', 'both'):
            markdown_path = f'{output}.md'
            generator.export_markdown(markdown_path)
            click.echo(f'Markdown documentation exported to: {markdown_path}')

        if output_format in ('pdf', 'both'):
            pdf_path = f'{output}.pdf'
            generator.export_pdf(pdf_path)
            click.echo(f'PDF documentation exported to: {pdf_path}')

        click.echo('Documentation export completed successfully!')

    except ImportFromStringError as e:
        click.echo(f'Import error: {e}', err=True)
    except ImportError as e:
        click.echo(f'Missing dependencies: {e}', err=True)
        click.echo('Install with: pip install markdown weasyprint jinja2', err=True)
    except Exception as e:
        traceback.print_exc()
        logger.error(f'Failed to export documentation: {e!s}')


if __name__ == '__main__':
    cli()
