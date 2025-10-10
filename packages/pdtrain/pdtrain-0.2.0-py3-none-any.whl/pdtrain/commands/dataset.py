"""Dataset management commands"""

import click
import time
import requests
import tarfile
import tempfile
from pathlib import Path
from pdtrain.client import APIClient
from pdtrain.utils.formatters import (
    format_table, format_size, format_timestamp,
    print_success, print_error, print_info, print_warning,
    console
)
from pdtrain.utils.progress import Spinner, ProgressBar


@click.group()
def dataset():
    """Manage training datasets"""
    pass


@dataset.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--name', required=True, help='Dataset name')
@click.option('--description', help='Dataset description')
@click.option('--exclude', multiple=True, help='Exclude pattern (can specify multiple, e.g., --exclude ".DS_Store" --exclude "*.tmp")')
@click.option('--wait', is_flag=True, help='Wait for validation')
@click.pass_context
def upload(ctx, path, name, description, exclude, wait):
    """Upload a dataset (file or directory)"""
    config = ctx.obj['config']

    if not config.is_configured():
        print_error("CLI not configured. Run 'pdtrain configure' first.")
        ctx.exit(1)

    client = APIClient(config.api_url, config.api_key)
    source_path = Path(path)

    # Default exclude patterns for datasets
    default_excludes = {
        '.DS_Store',
        'Thumbs.db',
        '.git',
        '.gitignore',
        '__MACOSX',
        '*.tmp',
        '*.cache'
    }

    # Combine default and user-specified excludes
    exclude_patterns = set(default_excludes)
    if exclude:
        exclude_patterns.update(exclude)

    def should_exclude(file_path: Path, base_path: Path) -> bool:
        """Check if file should be excluded based on patterns"""
        rel_path = file_path.relative_to(base_path)
        rel_path_str = str(rel_path)

        for pattern in exclude_patterns:
            # Check if any part of the path matches the pattern
            if pattern.startswith('*'):
                # Wildcard pattern (e.g., *.tmp)
                if rel_path_str.endswith(pattern[1:]):
                    return True
            elif pattern in rel_path.parts:
                # Directory name pattern (e.g., __MACOSX)
                return True
            elif rel_path_str == pattern or str(file_path.name) == pattern:
                # Exact match
                return True
        return False

    # Check if it's a directory or file
    temp_file = None
    if source_path.is_dir():
        # Create tar.gz from directory
        try:
            print_info(f"Creating tar.gz from directory {source_path.name}...")
            if exclude_patterns:
                print_info(f"Excluding patterns: {', '.join(sorted(exclude_patterns))}")

            # Create temporary tar.gz file
            temp_file = tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False)
            temp_path = Path(temp_file.name)
            temp_file.close()

            # Create tar.gz archive
            excluded_count = 0
            included_count = 0
            with tarfile.open(temp_path, 'w:gz') as tar:
                # Add all files from directory
                for item in source_path.rglob('*'):
                    if item.is_file():
                        # Check if file should be excluded
                        if should_exclude(item, source_path):
                            excluded_count += 1
                            continue

                        # Calculate relative path
                        arcname = item.relative_to(source_path)
                        tar.add(item, arcname=arcname)
                        included_count += 1

            if excluded_count > 0:
                print_info(f"Excluded {excluded_count} files, included {included_count} files")

            file_path = temp_path
            file_size = file_path.stat().st_size
            filename = f"{name}.tar.gz"
            file_ext = '.tar.gz'
            content_type = 'application/gzip'
            print_success(f"Created {filename} ({format_size(file_size)})")

        except Exception as e:
            print_error(f"Failed to create tar.gz: {str(e)}")
            if temp_file and Path(temp_file.name).exists():
                Path(temp_file.name).unlink()
            ctx.exit(1)

    else:
        # Use existing file
        file_path = source_path
        file_size = file_path.stat().st_size
        filename = file_path.name

        # Validate file extension
        supported_extensions = {'.csv', '.parquet', '.json', '.jsonl', '.zip', '.tar.gz', '.tgz'}
        file_ext = file_path.suffix.lower()
        if file_path.name.endswith('.tar.gz'):
            file_ext = '.tar.gz'

        if file_ext not in supported_extensions:
            print_error(f"Unsupported file format: {file_ext}")
            print_info(f"Supported formats: {', '.join(supported_extensions)} or directory")
            ctx.exit(1)

        # Determine content type
        content_type_map = {
            '.csv': 'text/csv',
            '.parquet': 'application/octet-stream',
            '.json': 'application/json',
            '.jsonl': 'application/x-ndjson',
            '.zip': 'application/zip',
            '.tar.gz': 'application/gzip',
            '.tgz': 'application/gzip',
        }
        content_type = content_type_map.get(file_ext, 'application/octet-stream')

    try:
        # Step 0: Check quota before upload
        with Spinner("Checking storage quota..."):
            quota = client.get_quota()
            datasets = quota.get('datasets', {})

            # Convert GB to bytes
            dataset_used_gb = datasets.get('current_storage_gb', 0)
            dataset_limit_gb = datasets.get('max_storage_gb', 0)
            dataset_used_bytes = int(dataset_used_gb * 1024 * 1024 * 1024)
            dataset_limit_bytes = int(dataset_limit_gb * 1024 * 1024 * 1024)
            available = dataset_limit_bytes - dataset_used_bytes

            if file_size > available:
                print_error(f"Insufficient dataset storage quota!")
                print_error(f"File size: {format_size(file_size)}")
                print_error(f"Available: {format_size(available)}")
                print_error(f"Used: {format_size(dataset_used_bytes)} / {format_size(dataset_limit_bytes)}")
                print_info("Delete old datasets to free up space or contact support to increase quota")

                # Clean up temp file if exists
                if temp_file and file_path.exists():
                    file_path.unlink()
                ctx.exit(1)

        print_success(f"Quota check passed ({format_size(available)} dataset storage available)")

        # Step 1: Get presigned URL
        with Spinner(f"Requesting upload URL for {filename}..."):
            presign = client.presign_dataset(
                dataset_name=name,
                files=[{
                    'path': filename,
                    'content_type': content_type
                }]
            )

        dataset_id = presign['dataset_id']
        version = presign['version']
        presigned_post = presign['presigned'][0]

        # Step 2: Upload to S3 using presigned POST
        print_info(f"Uploading {filename} ({format_size(file_size)})...")

        # Prepare form data for presigned POST
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f, content_type)}
            fields = presigned_post['fields']

            response = requests.post(presigned_post['url'], data=fields, files=files)
            response.raise_for_status()

        print_success("Upload complete")

        # Step 3: Finalize dataset
        with Spinner("Finalizing and validating dataset..."):
            finalize_result = client.finalize_dataset(
                dataset_id=dataset_id,
                version=version,
                size_bytes=file_size,
                num_files=1,
                set_current=True
            )

        # Check validation status
        validation = finalize_result.get('validation', {})
        validation_status = validation.get('status')

        if validation_status == 'passed':
            print_success("Validation passed")

            # Show metadata
            metadata = validation.get('metadata', {})
            if metadata.get('file_type'):
                print_info(f"✓ File type: {metadata['file_type']}")
            if metadata.get('row_count'):
                print_info(f"✓ Rows: {metadata['row_count']:,}")
            if metadata.get('column_count'):
                print_info(f"✓ Columns: {metadata['column_count']}")

            # Show warnings
            warnings = validation.get('warnings', [])
            if warnings:
                print_warning("Warnings:")
                for warning in warnings:
                    print_warning(f"  - {warning}")

        elif validation_status == 'failed':
            print_error("Validation failed")
            errors = validation.get('errors', [])
            for error in errors:
                print_error(f"  - {error}")

            # Clean up temp file if exists
            if temp_file and file_path.exists():
                file_path.unlink()
            ctx.exit(1)
        else:
            print_info(f"Validation status: {validation_status}")

        # Show dataset info
        click.echo(f"\nDataset ID: {dataset_id}")
        click.echo(f"Name: {name}")
        click.echo(f"Version: {version}")
        click.echo(f"Status: {finalize_result.get('status')}")

        if description:
            # Update description
            # Note: This would require a PATCH endpoint which we can add later
            pass

    except requests.exceptions.RequestException as e:
        print_error(f"Upload failed: {str(e)}")

        # Clean up temp file if exists
        if temp_file and file_path.exists():
            file_path.unlink()
        ctx.exit(1)
    except Exception as e:
        print_error(f"Upload failed: {str(e)}")

        # Clean up temp file if exists
        if temp_file and file_path.exists():
            file_path.unlink()
        ctx.exit(1)

    finally:
        # Clean up temp file after successful upload
        if temp_file and file_path.exists():
            file_path.unlink()


@dataset.command()
@click.option('--limit', default=50, help='Number of datasets to show')
@click.option('--name', help='Filter by name')
@click.pass_context
def list(ctx, limit, name):
    """List all datasets"""
    config = ctx.obj['config']

    if not config.is_configured():
        print_error("CLI not configured. Run 'pdtrain configure' first.")
        ctx.exit(1)

    client = APIClient(config.api_url, config.api_key)

    try:
        response = client.list_datasets(limit=limit, name=name)
        datasets = response.get('items', [])

        if not datasets:
            print_info("No datasets found")
            return

        # Simple list format - easy to copy IDs
        click.echo("\n" + "=" * 80)
        for d in datasets:
            dataset_id = d.get('id', 'N/A')
            dataset_name = d.get('name', 'N/A')
            version = d.get('current_version', 'N/A')
            visibility = d.get('visibility', 'private')
            created = format_timestamp(d.get('created_at', ''))

            # Color code visibility
            if visibility == 'public':
                visibility_display = f"[green]{visibility}[/green]"
            else:
                visibility_display = f"[cyan]{visibility}[/cyan]"

            console.print(f"[cyan]ID:[/cyan] {dataset_id}")
            console.print(f"[cyan]Name:[/cyan] {dataset_name}:v{version}  [cyan]Visibility:[/cyan] {visibility_display}  [cyan]Created:[/cyan] {created}")
            click.echo("-" * 80)

        click.echo(f"\nTotal: {response.get('total', len(datasets))} dataset(s)\n")

    except Exception as e:
        print_error(f"Failed to list datasets: {str(e)}")
        ctx.exit(1)


@dataset.command()
@click.argument('dataset_id')
@click.pass_context
def show(ctx, dataset_id):
    """Show dataset details"""
    config = ctx.obj['config']

    if not config.is_configured():
        print_error("CLI not configured. Run 'pdtrain configure' first.")
        ctx.exit(1)

    client = APIClient(config.api_url, config.api_key)

    try:
        dataset = client.get_dataset(dataset_id)

        click.echo(f"\nDataset: {dataset['id']}")
        click.echo(f"Name: {dataset.get('name', 'N/A')}")
        click.echo(f"Description: {dataset.get('description', 'N/A')}")
        click.echo(f"Current Version: {dataset.get('current_version', 'N/A')}")
        click.echo(f"Visibility: {dataset.get('visibility', 'private')}")
        click.echo(f"Created: {dataset.get('created_at', 'N/A')}")
        click.echo(f"Updated: {dataset.get('updated_at', 'N/A')}")

        if dataset.get('tags'):
            click.echo(f"Tags: {', '.join(dataset['tags'])}")

    except Exception as e:
        print_error(f"Failed to get dataset: {str(e)}")
        ctx.exit(1)


@dataset.command()
@click.argument('dataset_id')
@click.option('--version', type=int, default=1, help='Dataset version')
@click.option('--output', type=click.Path(), help='Output directory')
@click.pass_context
def download(ctx, dataset_id, version, output):
    """Download a dataset"""
    config = ctx.obj['config']

    if not config.is_configured():
        print_error("CLI not configured. Run 'pdtrain configure' first.")
        ctx.exit(1)

    client = APIClient(config.api_url, config.api_key)

    # Set output directory
    if output:
        output_dir = Path(output)
    else:
        output_dir = Path.cwd()

    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Get download URLs
        with Spinner("Fetching download URLs..."):
            download_info = client.download_dataset(dataset_id, version)

        files = download_info.get('files', [])

        if not files:
            print_info("No files found in dataset")
            return

        print_info(f"Downloading {len(files)} file(s)...")

        # Download each file
        for file_info in files:
            file_name = file_info['file_name']
            download_url = file_info['download_url']
            file_size = file_info['size_bytes']
            output_path = output_dir / file_name

            print_info(f"Downloading {file_name} ({format_size(file_size)})...")

            # Download file
            response = requests.get(download_url, stream=True)
            response.raise_for_status()

            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print_success(f"Saved to {output_path}")

        print_success(f"Downloaded {len(files)} file(s) to {output_dir}")

    except Exception as e:
        print_error(f"Download failed: {str(e)}")
        ctx.exit(1)


@dataset.command()
@click.argument('dataset_id')
@click.confirmation_option(prompt='Are you sure you want to delete this dataset?')
@click.pass_context
def delete(ctx, dataset_id):
    """Delete a dataset (all versions)"""
    config = ctx.obj['config']

    if not config.is_configured():
        print_error("CLI not configured. Run 'pdtrain configure' first.")
        ctx.exit(1)

    client = APIClient(config.api_url, config.api_key)

    try:
        with Spinner("Deleting dataset..."):
            client.delete_dataset(dataset_id)

        print_success(f"Dataset {dataset_id} deleted successfully")

    except Exception as e:
        print_error(f"Failed to delete dataset: {str(e)}")
        ctx.exit(1)
