"""Logs viewing commands"""

import click
import time
import json
from pdtrain.client import APIClient
from pdtrain.utils.formatters import print_error, print_info
from pdtrain.utils.progress import Spinner


@click.command()
@click.argument('run_id')
@click.option('--lines', default=300, help='Number of lines to show')
@click.option('--follow', is_flag=True, help='Follow logs in real-time')
@click.option('--stream', is_flag=True, help='Use streaming API (Server-Sent Events)')
@click.option('--interval', default=5, help='Polling interval for --follow (seconds, ignored with --stream)')
@click.pass_context
def logs(ctx, run_id, lines, follow, stream, interval):
    """View training logs"""
    config = ctx.obj['config']

    if not config.is_configured():
        print_error("CLI not configured. Run 'pdtrain configure' first.")
        ctx.exit(1)

    client = APIClient(config.api_url, config.api_key)

    try:
        if stream or (follow and stream):
            # Use SSE streaming
            print_info(f"Streaming logs for {run_id} (Ctrl+C to stop)\n")

            try:
                response = client.stream_logs(run_id)
                event_type = None

                for line in response.iter_lines(decode_unicode=True):
                    if not line:
                        continue

                    # Parse SSE format
                    if line.startswith('event: '):
                        event_type = line[7:].strip()
                    elif line.startswith('data: '):
                        data = json.loads(line[6:])

                        if event_type == 'log':
                            # Print log message
                            message = data.get('message', '').rstrip()
                            click.echo(message)
                        elif event_type == 'status':
                            # Print status update
                            status = data.get('status', 'unknown')
                            print_info(f"\n[Status: {status}]")
                        elif event_type == 'error':
                            # Print error
                            error = data.get('error', 'Unknown error')
                            print_error(f"\nError: {error}")
                            break
                        elif event_type == 'done':
                            # Stream finished
                            status = data.get('status', 'unknown')
                            message = data.get('message', '')
                            print_info(f"\n{message}")
                            break

                        event_type = None  # Reset

            except KeyboardInterrupt:
                print_info("\nStopped streaming logs")
            except Exception as e:
                print_error(f"Stream error: {str(e)}")
                ctx.exit(1)

        elif follow:
            # Follow mode - poll for new logs
            print_info(f"Following logs for {run_id} (Ctrl+C to stop)")
            print_info(f"Polling every {interval} seconds...\n")

            last_timestamp = None
            previous_status = None

            while True:
                try:
                    # Get logs
                    log_data = client.get_logs(run_id, limit=lines)

                    # Check run status from separate API call
                    try:
                        run_info = client.get_run(run_id)
                        current_status = run_info.get('status', 'unknown')
                    except:
                        current_status = 'unknown'

                    # Print new logs only
                    log_events = log_data.get('events', [])

                    for event in log_events:
                        event_timestamp = event.get('timestamp')
                        message = event.get('message', '').rstrip()

                        # Only show logs newer than last seen
                        if last_timestamp is None or event_timestamp > last_timestamp:
                            click.echo(message)
                            last_timestamp = event_timestamp

                    # Print status update if changed
                    if current_status != previous_status:
                        print_info(f"\nStatus: {current_status}")
                        previous_status = current_status

                    # Check if terminal state
                    if current_status in ['completed', 'failed', 'stopped']:
                        print_info(f"\nRun {current_status}. Exiting follow mode.")
                        break

                    # Wait before next poll
                    time.sleep(interval)

                except KeyboardInterrupt:
                    print_info("\nStopped following logs")
                    break

        else:
            # One-time fetch
            with Spinner("Fetching logs..."):
                log_data = client.get_logs(run_id, limit=lines)

            log_events = log_data.get('events', [])

            if not log_events:
                print_info("No logs available yet")
                return

            # Print all logs
            for event in log_events:
                message = event.get('message', '').rstrip()
                click.echo(message)

            # Show summary
            total_logs = len(log_events)
            click.echo(f"\n--- {total_logs} log lines (last {lines} requested) ---")

            # Get run status from separate API call
            try:
                run_info = client.get_run(run_id)
                status = run_info.get('status')
                if status:
                    click.echo(f"Run Status: {status}")
            except:
                pass

    except Exception as e:
        print_error(f"Failed to fetch logs: {str(e)}")
        ctx.exit(1)
