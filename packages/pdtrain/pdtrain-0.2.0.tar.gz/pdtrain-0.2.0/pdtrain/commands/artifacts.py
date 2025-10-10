"""Artifacts management commands"""

import click
import requests
from pathlib import Path
from pdtrain.client import APIClient
from pdtrain.utils.formatters import (
    format_table, format_size, format_timestamp,
    print_error, print_info, print_success
)
from pdtrain.utils.progress import Spinner


@click.group()
def artifacts():
    """Manage training artifacts"""
    pass


@artifacts.command()
@click.argument('run_id')
@click.pass_context
def list(ctx, run_id):
    """List run artifacts"""
    config = ctx.obj['config']

    if not config.is_configured():
        print_error("CLI not configured. Run 'pdtrain configure' first.")
        ctx.exit(1)

    client = APIClient(config.api_url, config.api_key)

    try:
        with Spinner("Fetching artifacts..."):
            result = client.list_artifacts(run_id)

        artifacts = result.get('artifacts', [])

        if not artifacts:
            print_info("No artifacts found for this run")
            return

        # Display artifacts table
        rows = []
        total_size = 0

        for artifact in artifacts:
            file_name = artifact.get('path', 'N/A')  # API returns 'path', not 'file_name'
            size_bytes = artifact.get('size_bytes', 0)
            last_modified = artifact.get('created_at', '')  # API returns 'created_at', not 'last_modified'

            rows.append([
                file_name,
                format_size(size_bytes),
                format_timestamp(last_modified)
            ])

            total_size += size_bytes

        format_table(
            headers=['FILE', 'SIZE', 'MODIFIED'],
            rows=rows,
            title=f"Artifacts for {run_id}"
        )

        click.echo(f"\nTotal: {len(artifacts)} files ({format_size(total_size)})")

    except Exception as e:
        print_error(f"Failed to list artifacts: {str(e)}")
        ctx.exit(1)


@artifacts.command()
@click.argument('run_id')
@click.option('--output', type=click.Path(), help='Output directory')
@click.pass_context
def download(ctx, run_id, output):
    """Download all artifacts"""
    config = ctx.obj['config']

    if not config.is_configured():
        print_error("CLI not configured. Run 'pdtrain configure' first.")
        ctx.exit(1)

    client = APIClient(config.api_url, config.api_key)

    # Set output directory
    if output:
        output_dir = Path(output)
    else:
        output_dir = Path.cwd() / 'artifacts' / run_id

    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Get artifact list with download URLs
        with Spinner("Fetching artifact URLs..."):
            result = client.list_artifacts(run_id)

        artifacts = result.get('artifacts', [])

        if not artifacts:
            print_info("No artifacts to download")
            return

        print_info(f"Downloading {len(artifacts)} artifact(s) to {output_dir}...")

        # Download each artifact
        for artifact in artifacts:
            file_path = artifact.get('path')  # API returns 'path', not 'file_name'
            download_url = artifact.get('url')  # API returns 'url', not 'download_url'
            size_bytes = artifact.get('size_bytes', 0)

            if not file_path or not download_url:
                print_error(f"Skipping artifact with missing info: {artifact}")
                continue

            # Preserve directory structure from path
            output_path = output_dir / file_path
            output_path.parent.mkdir(parents=True, exist_ok=True)

            file_name = output_path.name

            print_info(f"Downloading {file_name} ({format_size(size_bytes)})...")

            # Download file with streaming
            response = requests.get(download_url, stream=True)
            response.raise_for_status()

            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print_success(f"Saved to {output_path}")

        print_success(f"\nDownloaded {len(artifacts)} artifact(s) to {output_dir}")

    except Exception as e:
        print_error(f"Download failed: {str(e)}")
        ctx.exit(1)
