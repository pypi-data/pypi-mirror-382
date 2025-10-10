"""Bundle management commands"""

import click
import time
import tarfile
import tempfile
from pathlib import Path
from pdtrain.client import APIClient
from pdtrain.utils.formatters import (
    format_table, format_size, format_timestamp,
    print_success, print_error, print_info, print_warning,
    console
)
from pdtrain.utils.progress import Spinner


@click.group()
def bundle():
    """Manage training code bundles"""
    pass


@bundle.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--name', help='Bundle name (defaults to directory/filename)')
@click.option('--version', help='Bundle version')
@click.option('--exclude', multiple=True, help='Exclude pattern (can specify multiple, e.g., --exclude "*.pyc" --exclude "__pycache__")')
@click.option('--wait', is_flag=True, help='Wait for validation to complete')
@click.pass_context
def upload(ctx, path, name, version, exclude, wait):
    """Upload a training code bundle (file or directory)"""
    config = ctx.obj['config']

    if not config.is_configured():
        print_error("CLI not configured. Run 'pdtrain configure' first.")
        ctx.exit(1)

    client = APIClient(config.api_url, config.api_key)
    source_path = Path(path)

    # Default exclude patterns (common unnecessary files)
    default_excludes = {
        '__pycache__',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.Python',
        '*.so',
        '.git',
        '.gitignore',
        '.DS_Store',
        '*.egg-info',
        'dist',
        'build',
        '.pytest_cache',
        '.venv',
        'venv',
        '.env'
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
                # Wildcard pattern (e.g., *.pyc)
                if rel_path_str.endswith(pattern[1:]):
                    return True
            elif pattern in rel_path.parts:
                # Directory name pattern (e.g., __pycache__)
                return True
            elif rel_path_str == pattern or str(file_path.name) == pattern:
                # Exact match
                return True
        return False

    # Check if it's a directory or file
    if source_path.is_dir():
        # Create tar.gz from directory
        bundle_name = name or source_path.name
        temp_file = None

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
            filename = f"{bundle_name}.tar.gz"
            print_success(f"Created {filename} ({format_size(file_size)})")

        except Exception as e:
            print_error(f"Failed to create tar.gz: {str(e)}")
            if temp_file and Path(temp_file.name).exists():
                Path(temp_file.name).unlink()
            ctx.exit(1)

    else:
        # Use existing file
        file_path = source_path

        if not file_path.suffix in ['.gz', '.tgz', '.tar']:
            print_error("File must be .tar.gz, .tgz format, or a directory")
            ctx.exit(1)

        bundle_name = name or file_path.stem.replace('.tar', '')
        file_size = file_path.stat().st_size
        filename = file_path.name
        temp_file = None

    try:
        # Step 0: Check quota before upload
        with Spinner("Checking storage quota..."):
            quota = client.get_quota()
            bundles = quota.get('bundles', {})

            # Convert GB to bytes
            bundle_used_gb = bundles.get('current_storage_gb', 0)
            bundle_limit_gb = bundles.get('max_storage_gb', 0)
            bundle_used_bytes = int(bundle_used_gb * 1024 * 1024 * 1024)
            bundle_limit_bytes = int(bundle_limit_gb * 1024 * 1024 * 1024)
            available = bundle_limit_bytes - bundle_used_bytes

            if file_size > available:
                print_error(f"Insufficient bundle storage quota!")
                print_error(f"File size: {format_size(file_size)}")
                print_error(f"Available: {format_size(available)}")
                print_error(f"Used: {format_size(bundle_used_bytes)} / {format_size(bundle_limit_bytes)}")
                print_info("Delete old bundles to free up space or contact support to increase quota")

                # Clean up temp file if exists
                if temp_file and file_path.exists():
                    file_path.unlink()
                ctx.exit(1)

        print_success(f"Quota check passed ({format_size(available)} bundle storage available)")

        # Step 1: Get presigned URL
        with Spinner(f"Requesting upload URL for {filename}..."):
            presign = client.presign_bundle(
                filename=filename,
                content_type="application/gzip"
            )

        # Step 2: Upload to S3
        print_info(f"Uploading {filename} ({format_size(file_size)})...")
        client.upload_bundle(
            presigned_url=presign['presigned_url'],
            file_path=file_path,
            content_type="application/gzip"
        )
        print_success("Upload complete")

        # Step 3: Finalize bundle
        with Spinner("Finalizing bundle..."):
            bundle_data = client.finalize_bundle(s3_key=presign['s3_key'])

        bundle_id = bundle_data['id']
        print_success(f"Bundle finalized: {bundle_id}")

        # Step 4: Wait for validation if requested
        if wait:
            print_info("Waiting for validation...")
            max_attempts = 30
            for attempt in range(max_attempts):
                bundle_info = client.get_bundle(bundle_id)
                status = bundle_info.get('validation_status')

                if status == 'ready':
                    print_success("Validation passed")

                    # Show metadata
                    if bundle_info.get('has_requirements_txt'):
                        print_info("✓ requirements.txt found")
                    if bundle_info.get('entry_point_verified'):
                        print_info("✓ Entry point verified")
                    if bundle_info.get('total_files'):
                        print_info(f"✓ {bundle_info['total_files']} files")

                    # Show warnings
                    if bundle_info.get('validation_warnings'):
                        print_warning("Warnings:")
                        for warning in bundle_info['validation_warnings']:
                            print_warning(f"  - {warning}")
                    break
                elif status == 'failed':
                    print_error("Validation failed")
                    if bundle_info.get('validation_errors'):
                        for error in bundle_info['validation_errors']:
                            print_error(f"  - {error}")

                    # Clean up temp file if exists
                    if temp_file and file_path.exists():
                        file_path.unlink()
                    ctx.exit(1)
                elif status == 'validating':
                    time.sleep(2)
                else:
                    time.sleep(2)
            else:
                print_warning("Validation timeout - check status later")

        # Show bundle info
        click.echo(f"\nBundle ID: {bundle_id}")
        if bundle_data.get('name'):
            click.echo(f"Name: {bundle_data['name']}")
        if bundle_data.get('version'):
            click.echo(f"Version: {bundle_data['version']}")

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


@bundle.command()
@click.option('--full-id', is_flag=True, help='Show full bundle IDs')
@click.pass_context
def list(ctx, full_id):
    """List all bundles"""
    config = ctx.obj['config']

    if not config.is_configured():
        print_error("CLI not configured. Run 'pdtrain configure' first.")
        ctx.exit(1)

    client = APIClient(config.api_url, config.api_key)

    try:
        bundles = client.list_bundles()

        if not bundles:
            print_info("No bundles found")
            return

        # Simple list format - easy to copy
        click.echo("\n" + "=" * 80)
        for b in bundles:
            bundle_id = b.get('id', 'N/A')
            name = b.get('name', 'N/A')
            version = b.get('version', 'N/A')
            status = b.get('validation_status', 'unknown')
            size = format_size(b.get('size_bytes', 0))
            created = format_timestamp(b.get('created_at', ''))

            # Color code status
            if status == 'ready':
                status_display = f"[green]{status}[/green]"
            elif status == 'failed':
                status_display = f"[red]{status}[/red]"
            elif status == 'validating':
                status_display = f"[yellow]{status}[/yellow]"
            else:
                status_display = status

            console.print(f"[cyan]ID:[/cyan] {bundle_id}")
            console.print(f"[cyan]Name:[/cyan] {name}:{version}  [cyan]Status:[/cyan] {status_display}  [cyan]Size:[/cyan] {size}  [cyan]Created:[/cyan] {created}")
            click.echo("-" * 80)

        click.echo(f"\nTotal: {len(bundles)} bundle(s)\n")

    except Exception as e:
        print_error(f"Failed to list bundles: {str(e)}")
        ctx.exit(1)


@bundle.command()
@click.argument('bundle_id')
@click.pass_context
def show(ctx, bundle_id):
    """Show bundle details"""
    config = ctx.obj['config']

    if not config.is_configured():
        print_error("CLI not configured. Run 'pdtrain configure' first.")
        ctx.exit(1)

    client = APIClient(config.api_url, config.api_key)

    try:
        bundle = client.get_bundle(bundle_id)

        click.echo(f"\nBundle: {bundle['id']}")
        click.echo(f"Name: {bundle.get('name', 'N/A')}")
        click.echo(f"Version: {bundle.get('version', 'N/A')}")
        click.echo(f"Status: {bundle.get('validation_status', 'unknown')}")
        click.echo(f"Size: {format_size(bundle.get('size_bytes', 0))}")
        click.echo(f"Created: {bundle.get('created_at', 'N/A')}")

        if bundle.get('has_requirements_txt'):
            click.echo(f"Requirements: Yes")
        if bundle.get('entry_point_verified'):
            click.echo(f"Entry Point: Verified")
        if bundle.get('total_files'):
            click.echo(f"Files: {bundle['total_files']}")

        if bundle.get('validation_errors'):
            print_error("\nErrors:")
            for error in bundle['validation_errors']:
                print_error(f"  - {error}")

        if bundle.get('validation_warnings'):
            print_warning("\nWarnings:")
            for warning in bundle['validation_warnings']:
                print_warning(f"  - {warning}")

    except Exception as e:
        print_error(f"Failed to get bundle: {str(e)}")
        ctx.exit(1)
