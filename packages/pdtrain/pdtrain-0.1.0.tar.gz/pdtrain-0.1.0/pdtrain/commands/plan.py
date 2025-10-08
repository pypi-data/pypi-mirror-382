"""Plan commands for viewing plan information and limits"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TaskProgressColumn
from pdtrain.client import APIClient
from pdtrain.utils.formatters import (
    print_success, print_error, print_info, print_warning,
    console
)


@click.group()
def plan():
    """View plan information and limits"""
    pass


@plan.command()
@click.pass_context
def info(ctx):
    """
    Show comprehensive plan information

    Displays:
    - Plan details and tier
    - Wallet balance
    - Usage limits and current usage
    - Storage quota
    - Instance types and regions allowed

    Examples:

      # Show complete plan information
      pdtrain plan info
    """
    config = ctx.obj['config']

    if not config.is_configured():
        print_error("CLI not configured. Run 'pdtrain configure' first.")
        ctx.exit(1)

    client = APIClient(config.api_url, config.api_key)

    try:
        plan_info = client.get_plan_information()

        console.print("\n[bold cyan]═══ Your Plan ═══[/bold cyan]\n")

        # Plan Details
        plan_id = plan_info.get('plan_id', 'unknown')
        plan_name = plan_info.get('plan_name') or plan_id
        pricing_tier = plan_info.get('pricing_tier') or 'Standard'

        console.print(f"[bold]Plan:[/bold] {plan_name}")
        console.print(f"[bold]Plan ID:[/bold] {plan_id}")
        console.print(f"[bold]Tier:[/bold] {pricing_tier}\n")

        # Wallet Balance
        wallet = plan_info.get('wallet_balance', {})
        _display_wallet_summary(wallet)

        # Usage Summary
        limits = plan_info.get('limits_summary', {})
        usage_hours = limits.get('usage_hours', {})
        _display_usage_summary(usage_hours)

        # Storage Quota
        storage = limits.get('storage', {})
        _display_storage_summary(storage)

        # Compute Limits
        _display_compute_limits(limits)

        console.print()

    except Exception as e:
        print_error(f"Failed to get plan information: {str(e)}")
        ctx.exit(1)


@plan.command()
@click.pass_context
def limits(ctx):
    """
    Show detailed plan limits

    Examples:

      # Show all plan limits
      pdtrain plan limits
    """
    config = ctx.obj['config']

    if not config.is_configured():
        print_error("CLI not configured. Run 'pdtrain configure' first.")
        ctx.exit(1)

    client = APIClient(config.api_url, config.api_key)

    try:
        limits_data = client.get_plan_limits()

        console.print("\n[bold cyan]═══ Plan Limits ═══[/bold cyan]\n")

        # Concurrent Runs
        concurrent = limits_data.get('concurrent_runs', {})
        console.print("[bold yellow]Concurrent Runs[/bold yellow]")
        console.print(f"  Limit: {concurrent.get('limit', 0)}")
        console.print(f"  Current: {concurrent.get('current', 0)}")
        console.print(f"  Remaining: {concurrent.get('remaining', 0)}\n")

        # Usage Hours
        usage_hours = limits_data.get('usage_hours', {})
        _display_usage_summary(usage_hours)

        # Runtime
        runtime = limits_data.get('runtime', {})
        console.print("[bold yellow]Job Runtime[/bold yellow]")
        console.print(f"  Max per job: {runtime.get('limit_hours', 0)} hours ({runtime.get('limit_seconds', 0)} seconds)\n")

        # Storage
        storage = limits_data.get('storage', {})
        _display_storage_summary(storage)

        # Instance Types
        instances = limits_data.get('instance_types', {})
        console.print("[bold yellow]Instance Types[/bold yellow]")
        console.print(f"  Allowed patterns: {', '.join(instances.get('allowed_patterns', []))}")
        if instances.get('blocked_types'):
            console.print(f"  Blocked: {', '.join(instances.get('blocked_types', []))}")
        console.print()

        # Regions
        regions = limits_data.get('regions', {})
        console.print("[bold yellow]Regions[/bold yellow]")
        console.print(f"  Allowed: {', '.join(regions.get('allowed', []))}")
        console.print()

    except Exception as e:
        print_error(f"Failed to get plan limits: {str(e)}")
        ctx.exit(1)


@plan.command()
@click.pass_context
def usage(ctx):
    """
    Show usage summary and remaining quota

    Examples:

      # Show usage summary
      pdtrain plan usage
    """
    config = ctx.obj['config']

    if not config.is_configured():
        print_error("CLI not configured. Run 'pdtrain configure' first.")
        ctx.exit(1)

    client = APIClient(config.api_url, config.api_key)

    try:
        usage_data = client.get_plan_usage_summary()

        console.print("\n[bold cyan]═══ Usage Summary ═══[/bold cyan]\n")

        plan_id = usage_data.get('plan_id', 'unknown')
        console.print(f"[bold]Plan ID:[/bold] {plan_id}\n")

        # Usage Summary
        usage_summary = usage_data.get('usage_summary', {})
        limits = usage_data.get('limits', {})
        percentages = usage_data.get('usage_percentages', {})
        remaining = usage_data.get('remaining_usage', {})

        # Monthly Usage
        console.print("[bold yellow]Monthly Usage[/bold yellow]")
        monthly_used = usage_summary.get('monthly_usage_hours', 0)
        monthly_limit = limits.get('max_monthly_usage_hours')
        monthly_pct = percentages.get('monthly', 0)

        if monthly_limit:
            console.print(f"  Used: {monthly_used:.2f} hours / {monthly_limit} hours ({monthly_pct:.1f}%)")
            console.print(f"  Remaining: {remaining.get('monthly_hours', 0):.2f} hours")
            _display_usage_bar(monthly_pct)
        else:
            console.print(f"  Used: {monthly_used:.2f} hours (Unlimited)")
        console.print()

        # Total Usage
        console.print("[bold yellow]Total Usage[/bold yellow]")
        total_used = usage_summary.get('total_usage_hours', 0)
        total_limit = limits.get('max_total_usage_hours')
        total_pct = percentages.get('total', 0)

        if total_limit:
            console.print(f"  Used: {total_used:.2f} hours / {total_limit} hours ({total_pct:.1f}%)")
            console.print(f"  Remaining: {remaining.get('total_hours', 0):.2f} hours")
            _display_usage_bar(total_pct)
        else:
            console.print(f"  Used: {total_used:.2f} hours (Unlimited)")
        console.print()

        # Recent Usage (last 7 days)
        recent = usage_summary.get('recent_usage_hours', 0)
        console.print(f"[bold]Recent Usage (7 days):[/bold] {recent:.2f} hours\n")

        # Warnings
        if monthly_pct >= 80:
            print_warning(f"⚠ You've used {monthly_pct:.1f}% of your monthly quota!")
        if total_pct >= 80:
            print_warning(f"⚠ You've used {total_pct:.1f}% of your total quota!")

    except Exception as e:
        print_error(f"Failed to get usage summary: {str(e)}")
        ctx.exit(1)


@plan.command()
@click.pass_context
def storage(ctx):
    """
    Show storage quota and usage

    Examples:

      # Show storage quota
      pdtrain plan storage
    """
    config = ctx.obj['config']

    if not config.is_configured():
        print_error("CLI not configured. Run 'pdtrain configure' first.")
        ctx.exit(1)

    client = APIClient(config.api_url, config.api_key)

    try:
        storage_data = client.get_plan_storage_quota()

        console.print("\n[bold cyan]═══ Storage Quota ═══[/bold cyan]\n")

        plan_id = storage_data.get('plan_id', 'unknown')
        console.print(f"[bold]Plan ID:[/bold] {plan_id}\n")

        quota = storage_data.get('storage_quota', {})
        _display_storage_summary(quota)

    except Exception as e:
        print_error(f"Failed to get storage quota: {str(e)}")
        ctx.exit(1)


def _display_wallet_summary(wallet: dict):
    """Display wallet balance summary"""
    console.print("[bold yellow]Wallet Balance[/bold yellow]")

    balance = wallet.get('balance_usd', 0)
    reserved = wallet.get('reserved_balance_usd', 0)
    available = wallet.get('available_balance_usd', 0)

    console.print(f"  Total: ${balance:.2f}")
    console.print(f"  Reserved: ${reserved:.2f}")
    console.print(f"  Available: [bold green]${available:.2f}[/bold green]")

    if wallet.get('is_low_balance', False):
        threshold = wallet.get('low_balance_threshold_usd', 10)
        console.print(f"  [yellow]⚠ Balance below ${threshold:.2f} threshold[/yellow]")

    console.print()


def _display_usage_summary(usage_hours: dict):
    """Display usage hours summary"""
    console.print("[bold yellow]Usage Hours[/bold yellow]")

    # Monthly
    monthly = usage_hours.get('monthly', {})
    monthly_limit = monthly.get('limit')
    monthly_current = monthly.get('current', 0)
    monthly_remaining = monthly.get('remaining', 0)
    monthly_pct = monthly.get('percentage_used', 0)

    console.print("  [cyan]Monthly:[/cyan]")
    if monthly_limit:
        console.print(f"    Used: {monthly_current:.2f} / {monthly_limit} hours ({monthly_pct:.1f}%)")
        console.print(f"    Remaining: {monthly_remaining:.2f} hours")
        _display_usage_bar(monthly_pct, indent="    ")
    else:
        console.print(f"    Used: {monthly_current:.2f} hours (Unlimited)")

    # Total
    total = usage_hours.get('total', {})
    total_limit = total.get('limit')
    total_current = total.get('current', 0)
    total_remaining = total.get('remaining', 0)
    total_pct = total.get('percentage_used', 0)

    console.print("  [cyan]Total:[/cyan]")
    if total_limit:
        console.print(f"    Used: {total_current:.2f} / {total_limit} hours ({total_pct:.1f}%)")
        console.print(f"    Remaining: {total_remaining:.2f} hours")
        _display_usage_bar(total_pct, indent="    ")
    else:
        console.print(f"    Used: {total_current:.2f} hours (Unlimited)")

    console.print()


def _display_storage_summary(storage: dict):
    """Display storage quota summary"""
    console.print("[bold yellow]Storage Quota[/bold yellow]")

    # Datasets
    datasets = storage.get('datasets', {})
    ds_current = datasets.get('current_storage_gb', 0)
    ds_max = datasets.get('max_storage_gb', 0)
    ds_pct = datasets.get('storage_percentage_used', 0)
    ds_count = datasets.get('current_count', 0)
    ds_max_count = datasets.get('max_count', 0)

    console.print("  [cyan]Datasets:[/cyan]")
    console.print(f"    Storage: {ds_current:.2f} / {ds_max} GB ({ds_pct:.1f}%)")
    console.print(f"    Count: {ds_count} / {ds_max_count}")
    _display_usage_bar(ds_pct, indent="    ")

    # Bundles
    bundles = storage.get('bundles', {})
    b_current = bundles.get('current_storage_gb', 0)
    b_max = bundles.get('max_storage_gb', 0)
    b_pct = bundles.get('storage_percentage_used', 0)
    b_count = bundles.get('current_count', 0)

    console.print("  [cyan]Bundles:[/cyan]")
    console.print(f"    Storage: {b_current:.2f} / {b_max} GB ({b_pct:.1f}%)")
    console.print(f"    Count: {b_count}")
    _display_usage_bar(b_pct, indent="    ")

    # Limits
    limits = storage.get('limits', {})
    console.print("  [cyan]Limits:[/cyan]")
    console.print(f"    Max single dataset: {limits.get('max_single_dataset_size_gb', 0)} GB")
    console.print(f"    Max single bundle: {limits.get('max_single_bundle_size_mb', 0)} MB")
    console.print(f"    Dataset versions: {limits.get('max_dataset_versions_per_dataset', 0)}")
    console.print(f"    Retention: {limits.get('dataset_retention_days', 0)} days")

    console.print()


def _display_compute_limits(limits: dict):
    """Display compute limits"""
    console.print("[bold yellow]Compute Limits[/bold yellow]")

    # Concurrent runs
    concurrent = limits.get('concurrent_runs', {})
    console.print(f"  Max concurrent runs: {concurrent.get('limit', 0)}")

    # Runtime
    runtime = limits.get('runtime', {})
    console.print(f"  Max runtime per job: {runtime.get('limit_hours', 0)} hours")

    # Instance types
    instances = limits.get('instance_types', {})
    allowed = instances.get('allowed_patterns', [])
    console.print(f"  Allowed instances: {', '.join(allowed)}")

    # Regions
    regions = limits.get('regions', {})
    console.print(f"  Allowed regions: {', '.join(regions.get('allowed', []))}")


def _display_usage_bar(percentage: float, indent: str = ""):
    """Display a usage bar"""
    # Determine color based on percentage
    if percentage >= 90:
        color = "red"
    elif percentage >= 80:
        color = "yellow"
    elif percentage >= 60:
        color = "cyan"
    else:
        color = "green"

    # Create bar
    bar_width = 30
    filled = int((percentage / 100) * bar_width)
    bar = "█" * filled + "░" * (bar_width - filled)

    console.print(f"{indent}[{color}]{bar}[/{color}]")
