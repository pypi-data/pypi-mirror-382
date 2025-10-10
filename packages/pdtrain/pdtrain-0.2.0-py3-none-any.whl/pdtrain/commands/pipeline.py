"""Pipeline command for end-to-end training workflows"""

import click
import time
import tarfile
import tempfile
from pathlib import Path
from pdtrain.client import APIClient
from pdtrain.utils.formatters import (
    format_size, format_timestamp,
    print_success, print_error, print_info, print_warning,
    console
)
from pdtrain.utils.progress import Spinner


@click.group()
def pipeline():
    """End-to-end training pipelines"""
    pass


@pipeline.command()
@click.option('--bundle-path', required=True, type=click.Path(exists=True), help='Path to bundle (directory or .tar.gz)')
@click.option('--bundle-name', help='Bundle name (defaults to directory/file name)')
@click.option('--dataset-path', type=click.Path(exists=True), help='Path to dataset (file or directory)')
@click.option('--dataset-name', help='Dataset name (required if dataset-path provided)')
@click.option('--framework', help='Framework (pytorch, tensorflow, sklearn, xgboost, huggingface)')
@click.option('--framework-version', help='Framework version (e.g., 2.2.0)')
@click.option('--python-version', help='Python version (e.g., py310)')
@click.option('--image', help='Docker image URI (for custom container mode)')
@click.option('--entry', default='train.py', help='Entry point script')
@click.option('--env', multiple=True, help='Environment variable KEY=VALUE (can specify multiple)')
@click.option('--hyperparameter', multiple=True, help='Hyperparameter KEY=VALUE (can specify multiple)')
@click.option('--spot', is_flag=True, help='Use spot instances')
@click.option('--bundle-exclude', multiple=True, help='Bundle exclude pattern (can specify multiple)')
@click.option('--dataset-exclude', multiple=True, help='Dataset exclude pattern (can specify multiple)')
@click.option('--wait', is_flag=True, help='Wait for training completion')
@click.pass_context
def run(ctx, bundle_path, bundle_name, dataset_path, dataset_name, framework, framework_version,
        python_version, image, entry, env, hyperparameter, spot, bundle_exclude, dataset_exclude, wait):
    """
    Run complete training pipeline: upload bundle, upload dataset, create run, and submit.

    This command combines all steps into one:
    1. Upload bundle
    2. Upload dataset (optional)
    3. Create training run
    4. Submit to SageMaker

    Examples:

      # Minimal pipeline with PyTorch
      pdtrain pipeline run --bundle-path ./my-code --framework pytorch

      # Full pipeline with dataset and hyperparameters
      pdtrain pipeline run \\
        --bundle-path ./my-code \\
        --dataset-path ./data.csv \\
        --dataset-name "train-data" \\
        --framework pytorch \\
        --framework-version 2.2.0 \\
        --hyperparameter epochs=100 \\
        --hyperparameter batch_size=64 \\
        --wait
    """
    config = ctx.obj['config']

    if not config.is_configured():
        print_error("CLI not configured. Run 'pdtrain configure' first.")
        ctx.exit(1)

    # Validate dataset options
    if dataset_path and not dataset_name:
        print_error("--dataset-name is required when --dataset-path is provided")
        ctx.exit(1)

    client = APIClient(config.api_url, config.api_key)

    console.print("\n[bold cyan]═══ Training Pipeline ═══[/bold cyan]\n")

    # ============================================================
    # STEP 1: Upload Bundle
    # ============================================================
    console.print("[bold yellow]Step 1/4: Upload Bundle[/bold yellow]")

    bundle_id = _upload_bundle(
        client=client,
        path=bundle_path,
        name=bundle_name,
        exclude=bundle_exclude,
        ctx=ctx
    )

    if not bundle_id:
        print_error("Bundle upload failed")
        ctx.exit(1)

    print_success(f"✓ Bundle uploaded: {bundle_id}\n")

    # ============================================================
    # STEP 2: Upload Dataset (Optional)
    # ============================================================
    dataset_id = None
    if dataset_path:
        console.print("[bold yellow]Step 2/4: Upload Dataset[/bold yellow]")

        dataset_id = _upload_dataset(
            client=client,
            path=dataset_path,
            name=dataset_name,
            exclude=dataset_exclude,
            ctx=ctx
        )

        if not dataset_id:
            print_error("Dataset upload failed")
            ctx.exit(1)

        print_success(f"✓ Dataset uploaded: {dataset_id}\n")
    else:
        console.print("[bold yellow]Step 2/4: Upload Dataset[/bold yellow]")
        print_info("Skipped (no dataset provided)\n")

    # ============================================================
    # STEP 3: Create Run
    # ============================================================
    step_num = 3
    console.print(f"[bold yellow]Step {step_num}/4: Create Training Run[/bold yellow]")

    run_id = _create_run(
        client=client,
        bundle_id=bundle_id,
        dataset_id=dataset_id,
        framework=framework,
        framework_version=framework_version,
        python_version=python_version,
        image=image,
        entry=entry,
        env=env,
        hyperparameter=hyperparameter,
        spot=spot,
        ctx=ctx
    )

    if not run_id:
        print_error("Run creation failed")
        ctx.exit(1)

    print_success(f"✓ Run created: {run_id}\n")

    # ============================================================
    # STEP 4: Submit Run
    # ============================================================
    step_num = 4
    console.print(f"[bold yellow]Step {step_num}/4: Submit to SageMaker[/bold yellow]")

    success = _submit_run(client, run_id, wait, ctx)

    if not success:
        print_error("Run submission failed")
        ctx.exit(1)

    print_success(f"✓ Run submitted successfully\n")

    # ============================================================
    # Summary
    # ============================================================
    console.print("[bold green]═══ Pipeline Complete ═══[/bold green]\n")
    console.print(f"[cyan]Run ID:[/cyan] {run_id}")
    console.print(f"[cyan]Bundle ID:[/cyan] {bundle_id}")
    if dataset_id:
        console.print(f"[cyan]Dataset ID:[/cyan] {dataset_id}")

    console.print(f"\n[bold]Next steps:[/bold]")
    console.print(f"  • View logs: [cyan]pdtrain logs {run_id} --follow[/cyan]")
    console.print(f"  • Check status: [cyan]pdtrain run show {run_id}[/cyan]")
    console.print(f"  • Download artifacts: [cyan]pdtrain artifacts download {run_id}[/cyan]")
    console.print()


def _upload_bundle(client, path, name, exclude, ctx):
    """Upload bundle and return bundle ID"""
    source_path = Path(path)

    # Default exclude patterns
    default_excludes = {
        '__pycache__', '*.pyc', '*.pyo', '*.pyd', '.Python', '*.so',
        '.git', '.gitignore', '.DS_Store', '*.egg-info', 'dist', 'build',
        '.pytest_cache', '.venv', 'venv', '.env'
    }

    exclude_patterns = set(default_excludes)
    if exclude:
        exclude_patterns.update(exclude)

    def should_exclude(file_path: Path, base_path: Path) -> bool:
        """Check if file should be excluded"""
        rel_path = file_path.relative_to(base_path)
        rel_path_str = str(rel_path)

        for pattern in exclude_patterns:
            if pattern.startswith('*'):
                if rel_path_str.endswith(pattern[1:]):
                    return True
            elif pattern in rel_path.parts:
                return True
            elif rel_path_str == pattern or str(file_path.name) == pattern:
                return True
        return False

    # Handle directory vs file
    temp_file = None
    if source_path.is_dir():
        bundle_name = name or source_path.name

        try:
            print_info(f"Creating tar.gz from directory {source_path.name}...")

            temp_file = tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False)
            temp_path = Path(temp_file.name)
            temp_file.close()

            excluded_count = 0
            included_count = 0
            with tarfile.open(temp_path, 'w:gz') as tar:
                for item in source_path.rglob('*'):
                    if item.is_file():
                        if should_exclude(item, source_path):
                            excluded_count += 1
                            continue

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
            return None
    else:
        file_path = source_path

        if not file_path.suffix in ['.gz', '.tgz', '.tar']:
            print_error("File must be .tar.gz, .tgz format, or a directory")
            return None

        bundle_name = name or file_path.stem.replace('.tar', '')
        file_size = file_path.stat().st_size
        filename = file_path.name

    try:
        # Check quota
        with Spinner("Checking storage quota..."):
            quota = client.get_quota()
            bundles = quota.get('bundles', {})

            bundle_used_gb = bundles.get('current_storage_gb', 0)
            bundle_limit_gb = bundles.get('max_storage_gb', 0)
            bundle_used_bytes = int(bundle_used_gb * 1024 * 1024 * 1024)
            bundle_limit_bytes = int(bundle_limit_gb * 1024 * 1024 * 1024)
            available = bundle_limit_bytes - bundle_used_bytes

            if file_size > available:
                print_error(f"Insufficient bundle storage quota!")
                print_error(f"File size: {format_size(file_size)}")
                print_error(f"Available: {format_size(available)}")
                if temp_file and file_path.exists():
                    file_path.unlink()
                return None

        print_success(f"Quota check passed ({format_size(available)} available)")

        # Get presigned URL
        with Spinner(f"Requesting upload URL..."):
            presign = client.presign_bundle(
                filename=filename,
                content_type="application/gzip"
            )

        # Upload to S3
        print_info(f"Uploading {filename} ({format_size(file_size)})...")
        client.upload_bundle(
            presigned_url=presign['presigned_url'],
            file_path=file_path,
            content_type="application/gzip"
        )
        print_success("Upload complete")

        # Finalize
        with Spinner("Finalizing bundle..."):
            bundle_data = client.finalize_bundle(s3_key=presign['s3_key'])

        bundle_id = bundle_data['id']

        # Wait for validation
        print_info("Waiting for validation...")
        max_attempts = 30
        for attempt in range(max_attempts):
            bundle_info = client.get_bundle(bundle_id)
            status = bundle_info.get('validation_status')

            if status == 'ready':
                print_success("Validation passed")
                break
            elif status == 'failed':
                print_error("Validation failed")
                if bundle_info.get('validation_errors'):
                    for error in bundle_info['validation_errors']:
                        print_error(f"  - {error}")
                if temp_file and file_path.exists():
                    file_path.unlink()
                return None
            else:
                time.sleep(2)

        return bundle_id

    except Exception as e:
        print_error(f"Upload failed: {str(e)}")
        return None
    finally:
        if temp_file and file_path.exists():
            file_path.unlink()


def _upload_dataset(client, path, name, exclude, ctx):
    """Upload dataset and return dataset ID"""
    source_path = Path(path)

    # Default exclude patterns
    default_excludes = {
        '.DS_Store', 'Thumbs.db', '.git', '.gitignore',
        '__MACOSX', '*.tmp', '*.cache'
    }

    exclude_patterns = set(default_excludes)
    if exclude:
        exclude_patterns.update(exclude)

    def should_exclude(file_path: Path, base_path: Path) -> bool:
        """Check if file should be excluded"""
        rel_path = file_path.relative_to(base_path)
        rel_path_str = str(rel_path)

        for pattern in exclude_patterns:
            if pattern.startswith('*'):
                if rel_path_str.endswith(pattern[1:]):
                    return True
            elif pattern in rel_path.parts:
                return True
            elif rel_path_str == pattern or str(file_path.name) == pattern:
                return True
        return False

    # Handle directory vs file
    temp_file = None
    if source_path.is_dir():
        try:
            print_info(f"Creating tar.gz from directory {source_path.name}...")

            temp_file = tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False)
            temp_path = Path(temp_file.name)
            temp_file.close()

            excluded_count = 0
            included_count = 0
            with tarfile.open(temp_path, 'w:gz') as tar:
                for item in source_path.rglob('*'):
                    if item.is_file():
                        if should_exclude(item, source_path):
                            excluded_count += 1
                            continue

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
            return None
    else:
        file_path = source_path
        file_size = file_path.stat().st_size
        filename = file_path.name

        # Validate extension
        supported_extensions = {'.csv', '.parquet', '.json', '.jsonl', '.zip', '.tar.gz', '.tgz'}
        file_ext = file_path.suffix.lower()
        if file_path.name.endswith('.tar.gz'):
            file_ext = '.tar.gz'

        if file_ext not in supported_extensions:
            print_error(f"Unsupported file format: {file_ext}")
            return None

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
        # Check quota
        with Spinner("Checking storage quota..."):
            quota = client.get_quota()
            datasets = quota.get('datasets', {})

            dataset_used_gb = datasets.get('current_storage_gb', 0)
            dataset_limit_gb = datasets.get('max_storage_gb', 0)
            dataset_used_bytes = int(dataset_used_gb * 1024 * 1024 * 1024)
            dataset_limit_bytes = int(dataset_limit_gb * 1024 * 1024 * 1024)
            available = dataset_limit_bytes - dataset_used_bytes

            if file_size > available:
                print_error(f"Insufficient dataset storage quota!")
                print_error(f"File size: {format_size(file_size)}")
                print_error(f"Available: {format_size(available)}")
                if temp_file and file_path.exists():
                    file_path.unlink()
                return None

        print_success(f"Quota check passed ({format_size(available)} available)")

        # Get presigned URL
        with Spinner("Requesting upload URL..."):
            presign = client.presign_dataset(
                filename=filename,
                content_type=content_type
            )

        # Upload to S3
        print_info(f"Uploading {filename} ({format_size(file_size)})...")
        client.upload_dataset(
            presigned_url=presign['presigned_url'],
            file_path=file_path,
            content_type=content_type
        )
        print_success("Upload complete")

        # Finalize
        with Spinner("Finalizing dataset..."):
            dataset_data = client.finalize_dataset(
                s3_key=presign['s3_key'],
                name=name,
                description=None
            )

        dataset_id = dataset_data['id']

        # Wait for validation
        print_info("Waiting for validation...")
        max_attempts = 30
        for attempt in range(max_attempts):
            dataset_info = client.get_dataset(dataset_id)
            status = dataset_info.get('validation_status')

            if status == 'ready':
                print_success("Validation passed")
                break
            elif status == 'failed':
                print_error("Validation failed")
                if dataset_info.get('validation_errors'):
                    for error in dataset_info['validation_errors']:
                        print_error(f"  - {error}")
                if temp_file and file_path.exists():
                    file_path.unlink()
                return None
            else:
                time.sleep(2)

        return dataset_id

    except Exception as e:
        print_error(f"Upload failed: {str(e)}")
        return None
    finally:
        if temp_file and file_path.exists():
            file_path.unlink()


def _create_run(client, bundle_id, dataset_id, framework, framework_version,
                python_version, image, entry, env, hyperparameter, spot, ctx):
    """Create training run and return run ID"""

    # Build payload
    payload = {
        'bundle_id': bundle_id,
        'entry': entry,
    }

    # Add framework or image
    if framework:
        payload['framework'] = framework
        if framework_version:
            payload['framework_version'] = framework_version
        if python_version:
            payload['python_version'] = python_version
        if spot:
            payload['spot_instances'] = True
    elif image:
        payload['image'] = image
    else:
        # Default to PyTorch
        payload['framework'] = 'pytorch'

    # Parse environment variables
    if env:
        env_dict = {}
        for e in env:
            if '=' in e:
                key, value = e.split('=', 1)
                env_dict[key] = value
        payload['env'] = env_dict

    # Parse hyperparameters
    if hyperparameter:
        hyperparam_dict = {}
        for hp in hyperparameter:
            if '=' in hp:
                key, value = hp.split('=', 1)
                try:
                    value = float(value) if '.' in value else int(value)
                except ValueError:
                    pass
                hyperparam_dict[key] = value
        payload['hyperparameters'] = hyperparam_dict

    # Add dataset if provided
    if dataset_id:
        payload['inputs'] = [{
            'type': 'dataset',
            'dataset_id': dataset_id,
            'version': 1
        }]

    try:
        with Spinner("Creating training run..."):
            run_data = client.create_run(payload)

        run_id = run_data['id']

        print_info(f"Status: {run_data.get('status')}")
        print_info(f"Framework: {run_data.get('framework', 'N/A')} {run_data.get('framework_version', '')}")
        print_info(f"Instance: {run_data.get('instance_type', 'N/A')}")

        return run_id

    except Exception as e:
        print_error(f"Failed to create run: {str(e)}")
        return None


def _submit_run(client, run_id, wait, ctx):
    """Submit run to SageMaker"""

    try:
        print_info("Submitting to SageMaker...")
        submit_result = client.submit_run(run_id)

        # Poll for job ARN
        if submit_result.get('status') == 'submitting':
            print_info("Waiting for job ARN...")
            max_wait = 60
            poll_interval = 2
            elapsed = 0

            while elapsed < max_wait:
                time.sleep(poll_interval)
                elapsed += poll_interval

                try:
                    run_data = client.get_run(run_id)
                    current_status = run_data.get('status')

                    if current_status in ['pending', 'running']:
                        job_arn = run_data.get('job_arn', 'N/A')
                        print_success(f"Job ARN: {job_arn}")
                        break
                    elif current_status == 'failed':
                        error_msg = run_data.get('error_message', 'Unknown error')
                        print_error(f"Submission failed: {error_msg}")
                        return False
                except Exception:
                    pass
            else:
                print_warning("Submission taking longer than expected")
        else:
            print_success(f"Job ARN: {submit_result.get('job_arn', 'N/A')}")

        # Wait for completion if requested
        if wait:
            print_info("Waiting for training to complete...")
            _wait_for_completion(client, run_id)

        return True

    except Exception as e:
        print_error(f"Failed to submit run: {str(e)}")
        return False


def _wait_for_completion(client, run_id):
    """Wait for run to complete"""
    print_info("Monitoring run status (press Ctrl+C to stop watching)...")

    try:
        last_status = None
        while True:
            run_data = client.get_run(run_id)
            status = run_data.get('status')

            if status != last_status:
                console.print(f"Status: [cyan]{status}[/cyan]")
                last_status = status

            if status in ['completed', 'failed', 'stopped']:
                if status == 'completed':
                    print_success("Training completed successfully!")
                elif status == 'failed':
                    error_msg = run_data.get('error_message', 'Unknown error')
                    print_error(f"Training failed: {error_msg}")
                else:
                    print_warning("Training was stopped")
                break

            time.sleep(10)
    except KeyboardInterrupt:
        print_info("\nStopped watching (training continues in background)")
