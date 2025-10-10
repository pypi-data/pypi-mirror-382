"""Storage quota commands"""

import click
from pdtrain.client import APIClient
from pdtrain.utils.formatters import format_size, print_error, print_info
from rich.console import Console
from rich.panel import Panel


console = Console()


@click.command()
@click.pass_context
def quota(ctx):
    """Show storage quota information"""
    config = ctx.obj['config']

    if not config.is_configured():
        print_error("CLI not configured. Run 'pdtrain configure' first.")
        ctx.exit(1)

    client = APIClient(config.api_url, config.api_key)

    try:
        quota_data = client.get_quota()

        # Extract nested data
        datasets = quota_data.get('datasets', {})
        bundles = quota_data.get('bundles', {})
        limits = quota_data.get('limits', {})

        # Format quota information
        content = []
        content.append("[bold cyan]Storage Quota[/bold cyan]\n")

        # Dataset storage (convert GB to bytes for display)
        dataset_used_gb = datasets.get('current_storage_gb', 0)
        dataset_limit_gb = datasets.get('max_storage_gb', 0)
        dataset_pct = datasets.get('storage_percentage_used', 0)
        dataset_used_bytes = int(dataset_used_gb * 1024 * 1024 * 1024)
        dataset_limit_bytes = int(dataset_limit_gb * 1024 * 1024 * 1024)

        content.append(f"Datasets: {format_size(dataset_used_bytes)} / {format_size(dataset_limit_bytes)} ({dataset_pct:.1f}%)")

        # Bundle storage (convert GB to bytes for display)
        bundle_used_gb = bundles.get('current_storage_gb', 0)
        bundle_limit_gb = bundles.get('max_storage_gb', 0)
        bundle_pct = bundles.get('storage_percentage_used', 0)
        bundle_used_bytes = int(bundle_used_gb * 1024 * 1024 * 1024)
        bundle_limit_bytes = int(bundle_limit_gb * 1024 * 1024 * 1024)

        content.append(f"Bundles: {format_size(bundle_used_bytes)} / {format_size(bundle_limit_bytes)} ({bundle_pct:.1f}%)")

        # Dataset count
        dataset_count = datasets.get('current_count', 0)
        dataset_count_limit = datasets.get('max_count', 0)
        content.append(f"\nDataset Count: {dataset_count} / {dataset_count_limit}")

        # Bundle count
        bundle_count = bundles.get('current_count', 0)
        content.append(f"Bundle Count: {bundle_count}")

        # Limits
        content.append(f"\n[bold]Limits:[/bold]")
        max_single_dataset_gb = limits.get('max_single_dataset_size_gb', 0)
        max_single_bundle_mb = limits.get('max_single_bundle_size_mb', 0)
        content.append(f"Max Dataset Size: {max_single_dataset_gb} GB")
        content.append(f"Max Bundle Size: {max_single_bundle_mb} MB")

        if limits.get('dataset_retention_days'):
            content.append(f"Dataset Retention: {limits['dataset_retention_days']} days")

        console.print(Panel("\n".join(content), border_style="cyan"))

        # Warnings
        if dataset_pct > 80:
            print_info("⚠️  Dataset storage is over 80% - consider cleaning up old datasets")
        if bundle_pct > 80:
            print_info("⚠️  Bundle storage is over 80% - consider removing old bundles")

    except Exception as e:
        print_error(f"Failed to get quota: {str(e)}")
        ctx.exit(1)
