"""Training run commands"""

import click
import time
from pdtrain.client import APIClient
from pdtrain.utils.formatters import (
    format_table, format_size, format_duration, format_timestamp,
    print_success, print_error, print_info, print_warning
)
from pdtrain.utils.progress import Spinner


@click.group()
def run():
    """Manage training runs"""
    pass


@run.command()
@click.option('--bundle', help='Bundle ID (from "pdtrain bundle list") - required for Script Mode')
@click.option('--dataset', multiple=True, help='Dataset ID (from "pdtrain dataset list") - can specify multiple')
@click.option('--framework', help='Framework (pytorch, tensorflow, sklearn, xgboost, huggingface) - for Script Mode')
@click.option('--framework-version', help='Framework version (e.g., 2.2.0)')
@click.option('--python-version', help='Python version (e.g., py310)')
@click.option('--image', help='Docker image URI (for Docker Mode - alternative to framework)')
@click.option('--entry', default='train.py', help='Entry point script')
@click.option('--env', multiple=True, help='Environment variable KEY=VALUE (can specify multiple)')
@click.option('--hyperparameter', multiple=True, help='Hyperparameter KEY=VALUE (can specify multiple)')
@click.option('--spot', is_flag=True, help='Use spot instances')
@click.option('--submit', is_flag=True, help='Submit immediately after creation')
@click.option('--wait', is_flag=True, help='Wait for completion (implies --submit)')
@click.pass_context
def create(ctx, bundle, dataset, framework, framework_version, python_version, image, entry, env, hyperparameter, spot, submit, wait):
    """Create a training run

    Two execution modes:
    1. Script Mode: Requires --bundle and --framework (or uses default PyTorch)
    2. Docker Mode: Requires --image (bundle optional if code is in image)
    """
    config = ctx.obj['config']

    if not config.is_configured():
        print_error("CLI not configured. Run 'pdtrain configure' first.")
        ctx.exit(1)

    # Validate execution mode
    if not bundle and not image and not framework:
        print_error("Must specify at least one of: --bundle, --image, or --framework")
        ctx.exit(1)

    if framework and image:
        print_error("Cannot specify both --framework and --image. Use --framework for Script Mode or --image for Docker Mode.")
        ctx.exit(1)

    client = APIClient(config.api_url, config.api_key)

    # Build run payload
    payload = {
        'entry': entry,
    }

    # Add bundle if provided
    if bundle:
        payload['bundle_id'] = bundle

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
        # Default to PyTorch if neither specified
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
                # Try to convert to number
                try:
                    value = float(value) if '.' in value else int(value)
                except ValueError:
                    pass
                hyperparam_dict[key] = value
        payload['hyperparameters'] = hyperparam_dict

    # Parse datasets (use IDs from 'pdtrain dataset list')
    if dataset:
        inputs = []
        for ds in dataset:
            # Dataset should be just the ID
            # Note: version is required by API, using 1 as default (current version)
            inputs.append({
                'type': 'dataset',
                'dataset_id': ds,
                'version': 1
            })
        payload['inputs'] = inputs

    try:
        # Create run
        with Spinner("Creating training run..."):
            run_data = client.create_run(payload)

        run_id = run_data['id']
        print_success(f"Run created: {run_id}")

        # Show run details
        click.echo(f"\nRun ID: {run_id}")
        click.echo(f"Status: {run_data.get('status')}")
        click.echo(f"Execution Mode: {run_data.get('execution_mode', 'N/A')}")
        if run_data.get('framework'):
            click.echo(f"Framework: {run_data['framework']} {run_data.get('framework_version', '')}")
        if run_data.get('image'):
            click.echo(f"Image: {run_data['image']}")
        click.echo(f"Instance: {run_data.get('instance_type', 'N/A')}")
        click.echo(f"Region: {run_data.get('region', 'N/A')}")

        # Submit if requested
        if submit or wait:
            print_info("Submitting to SageMaker...")
            submit_result = client.submit_run(run_id)

            # The API now returns immediately with "submitting" status
            # Poll for the actual job ARN
            if submit_result.get('status') == 'submitting':
                print_info("Submission in progress, waiting for job ARN...")
                max_wait = 60  # Wait up to 60 seconds for submission to complete
                poll_interval = 2
                elapsed = 0

                while elapsed < max_wait:
                    time.sleep(poll_interval)
                    elapsed += poll_interval

                    try:
                        run_data = client.get_run(run_id)
                        current_status = run_data.get('status')

                        if current_status in ['pending', 'running']:
                            # Submission completed
                            job_arn = run_data.get('job_arn', 'N/A')
                            print_success(f"Submitted - Job ARN: {job_arn}")
                            break
                        elif current_status == 'submitting':
                            # Still submitting, continue polling
                            continue
                        elif current_status == 'failed':
                            # Submission may have failed, but wait to confirm
                            # The background poller might recover the job status
                            continue
                    except Exception as e:
                        # Continue polling on transient errors
                        pass
                else:
                    # Timeout waiting for submission
                    print_warning("Submission taking longer than expected. Job may still be starting in background.")
            else:
                # Old API response format (if still present)
                print_success(f"Submitted - Job ARN: {submit_result.get('job_arn', 'N/A')}")

            # Wait if requested
            if wait:
                _wait_for_completion(client, run_id)

    except Exception as e:
        print_error(f"Failed to create run: {str(e)}")
        ctx.exit(1)


@run.command()
@click.argument('run_id')
@click.pass_context
def submit(ctx, run_id):
    """Submit a run to SageMaker"""
    config = ctx.obj['config']

    if not config.is_configured():
        print_error("CLI not configured. Run 'pdtrain configure' first.")
        ctx.exit(1)

    client = APIClient(config.api_url, config.api_key)

    try:
        with Spinner("Submitting run to SageMaker..."):
            result = client.submit_run(run_id)

        print_success(f"Run submitted: {run_id}")

        # The API now returns immediately with "submitting" status
        # Poll for the actual job ARN
        if result.get('status') == 'submitting':
            print_info("Submission in progress, waiting for job ARN...")
            max_wait = 60  # Wait up to 60 seconds
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
                        click.echo(f"Job ARN: {job_arn}")
                        click.echo(f"Status: {current_status}")
                        break
                    elif current_status == 'submitting':
                        # Still submitting, continue polling
                        continue
                    elif current_status == 'failed':
                        # Submission may have failed, but wait to confirm
                        # The background poller might recover the job status
                        continue
                except Exception:
                    # Continue polling on transient errors
                    pass
            else:
                # Timeout
                print_warning("Submission taking longer than expected. Job may still be starting.")
                click.echo(f"Status: submitting")
        else:
            # Old API format or already completed
            click.echo(f"Job ARN: {result.get('job_arn', 'N/A')}")
            click.echo(f"Status: {result.get('status')}")

    except Exception as e:
        print_error(f"Failed to submit run: {str(e)}")
        ctx.exit(1)


@run.command()
@click.option('--limit', default=50, help='Number of runs to show')
@click.option('--status', help='Filter by status')
@click.pass_context
def list(ctx, limit, status):
    """List all runs"""
    config = ctx.obj['config']

    if not config.is_configured():
        print_error("CLI not configured. Run 'pdtrain configure' first.")
        ctx.exit(1)

    client = APIClient(config.api_url, config.api_key)

    try:
        runs = client.list_runs(limit=limit)

        if not runs:
            print_info("No runs found")
            return

        # Filter by status if provided
        if status:
            runs = [r for r in runs if r.get('status', '').lower() == status.lower()]

        rows = []
        for r in runs:
            run_status = r.get('status', 'unknown')
            runtime = format_duration(r.get('runtime_seconds', 0)) if r.get('runtime_seconds') else '-'
            cost = f"${r.get('total_cost_usd', 0):.2f}" if r.get('total_cost_usd') else '-'

            rows.append([
                r.get('id', 'N/A')[:12] + '...',  # Truncate ID
                run_status,
                r.get('instance_type', 'N/A'),
                runtime,
                cost,
                format_timestamp(r.get('created_at', ''))
            ])

        format_table(
            headers=['ID', 'STATUS', 'INSTANCE', 'RUNTIME', 'COST', 'CREATED'],
            rows=rows,
            title=f"Runs ({len(runs)} shown)"
        )

    except Exception as e:
        print_error(f"Failed to list runs: {str(e)}")
        ctx.exit(1)


@run.command()
@click.argument('run_id')
@click.pass_context
def show(ctx, run_id):
    """Show run details"""
    config = ctx.obj['config']

    if not config.is_configured():
        print_error("CLI not configured. Run 'pdtrain configure' first.")
        ctx.exit(1)

    client = APIClient(config.api_url, config.api_key)

    try:
        run_data = client.get_run(run_id)

        click.echo(f"\nRun: {run_data['id']}")
        click.echo(f"Status: {run_data.get('status', 'unknown')}")
        click.echo(f"Execution Mode: {run_data.get('execution_mode', 'N/A')}")

        if run_data.get('framework'):
            click.echo(f"Framework: {run_data['framework']} {run_data.get('framework_version', '')}")
        if run_data.get('image'):
            click.echo(f"Image: {run_data['image']}")

        click.echo(f"Instance Type: {run_data.get('instance_type', 'N/A')}")
        click.echo(f"Region: {run_data.get('region', 'N/A')}")

        if run_data.get('started_at'):
            click.echo(f"Started: {run_data['started_at']}")
        if run_data.get('ended_at'):
            click.echo(f"Ended: {run_data['ended_at']}")
        if run_data.get('runtime_seconds'):
            click.echo(f"Runtime: {format_duration(run_data['runtime_seconds'])}")

        if run_data.get('total_cost_usd'):
            click.echo(f"\nCost: ${run_data['total_cost_usd']:.4f}")
        if run_data.get('commission_amount_usd'):
            click.echo(f"Commission: ${run_data['commission_amount_usd']:.4f}")

        if run_data.get('error_message'):
            print_error(f"\nError: {run_data['error_message']}")

        # Show bundle info
        if run_data.get('bundle'):
            bundle = run_data['bundle']
            click.echo(f"\nBundle: {bundle.get('id', 'N/A')}")
            click.echo(f"Bundle S3: {bundle.get('s3_uri', 'N/A')}")

    except Exception as e:
        print_error(f"Failed to get run: {str(e)}")
        ctx.exit(1)


@run.command()
@click.argument('run_id')
@click.option('--interval', default=10, help='Polling interval in seconds')
@click.pass_context
def watch(ctx, run_id, interval):
    """Watch run progress in real-time"""
    config = ctx.obj['config']

    if not config.is_configured():
        print_error("CLI not configured. Run 'pdtrain configure' first.")
        ctx.exit(1)

    client = APIClient(config.api_url, config.api_key)

    print_info(f"Watching run {run_id} (Ctrl+C to stop)")
    print_info(f"Polling every {interval} seconds...\n")

    try:
        previous_status = None
        refresh_errors = 0
        max_refresh_errors = 3  # Stop trying to refresh after 3 consecutive errors

        while True:
            # Try to refresh status (best effort - may fail if API is down)
            if refresh_errors < max_refresh_errors:
                try:
                    client.refresh_run(run_id)
                    refresh_errors = 0  # Reset on success
                except Exception as e:
                    refresh_errors += 1
                    if refresh_errors == 1:
                        print_warning(f"Failed to refresh from SageMaker (will retry): {str(e)}")
                    elif refresh_errors >= max_refresh_errors:
                        print_warning("Refresh repeatedly failing - will only show cached status")

            # Get current run data
            try:
                run_data = client.get_run(run_id)
            except Exception as e:
                print_error(f"Failed to get run status: {str(e)}")
                time.sleep(interval)
                continue

            current_status = run_data.get('status')

            # Print status update if changed
            if current_status != previous_status:
                timestamp = time.strftime('%H:%M:%S')
                click.echo(f"[{timestamp}] Status: {current_status}")

                if run_data.get('runtime_seconds'):
                    click.echo(f"          Runtime: {format_duration(run_data['runtime_seconds'])}")

                previous_status = current_status

            # Check if terminal state
            if current_status in ['completed', 'failed', 'stopped']:
                click.echo()
                if current_status == 'completed':
                    print_success(f"Run completed successfully!")
                    if run_data.get('total_cost_usd'):
                        click.echo(f"Total Cost: ${run_data['total_cost_usd']:.4f}")
                elif current_status == 'failed':
                    print_error(f"Run failed")
                    if run_data.get('error_message'):
                        print_error(f"Error: {run_data['error_message']}")
                else:
                    print_warning(f"Run stopped")

                break

            # Wait before next poll
            time.sleep(interval)

    except KeyboardInterrupt:
        print_info("\nStopped watching (run continues in background)")
    except Exception as e:
        print_error(f"Failed to watch run: {str(e)}")
        ctx.exit(1)


@run.command()
@click.argument('run_id')
@click.confirmation_option(prompt='Are you sure you want to stop this run?')
@click.pass_context
def stop(ctx, run_id):
    """Stop a running training job"""
    config = ctx.obj['config']

    if not config.is_configured():
        print_error("CLI not configured. Run 'pdtrain configure' first.")
        ctx.exit(1)

    client = APIClient(config.api_url, config.api_key)

    try:
        with Spinner("Stopping run..."):
            result = client.stop_run(run_id)

        print_success(f"Run stopped: {run_id}")
        click.echo(f"Status: {result.get('status')}")

    except Exception as e:
        print_error(f"Failed to stop run: {str(e)}")
        ctx.exit(1)


@run.command()
@click.argument('run_id')
@click.pass_context
def refresh(ctx, run_id):
    """Refresh run status from SageMaker"""
    config = ctx.obj['config']

    if not config.is_configured():
        print_error("CLI not configured. Run 'pdtrain configure' first.")
        ctx.exit(1)

    client = APIClient(config.api_url, config.api_key)

    try:
        with Spinner("Refreshing run status..."):
            result = client.refresh_run(run_id)

        print_success(f"Run status refreshed")
        click.echo(f"Status: {result.get('status')}")

    except Exception as e:
        print_error(f"Failed to refresh run: {str(e)}")
        ctx.exit(1)


def _wait_for_completion(client: APIClient, run_id: str, poll_interval: int = 10):
    """Helper function to wait for run completion"""
    print_info(f"Waiting for run to complete (polling every {poll_interval}s)...")

    previous_status = None

    while True:
        # Refresh and get status
        client.refresh_run(run_id)
        run_data = client.get_run(run_id)
        current_status = run_data.get('status')

        # Print update if status changed
        if current_status != previous_status:
            timestamp = time.strftime('%H:%M:%S')
            click.echo(f"[{timestamp}] Status: {current_status}")
            previous_status = current_status

        # Check terminal state
        if current_status in ['completed', 'failed', 'stopped']:
            click.echo()
            if current_status == 'completed':
                print_success("Training completed successfully!")
                if run_data.get('runtime_seconds'):
                    click.echo(f"Runtime: {format_duration(run_data['runtime_seconds'])}")
                if run_data.get('total_cost_usd'):
                    click.echo(f"Cost: ${run_data['total_cost_usd']:.4f}")
            elif current_status == 'failed':
                print_error("Training failed")
                if run_data.get('error_message'):
                    print_error(f"Error: {run_data['error_message']}")
            else:
                print_warning("Training stopped")
            break

        time.sleep(poll_interval)
