"""Wallet commands for managing wallet balance and transactions"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pdtrain.client import APIClient
from pdtrain.utils.formatters import (
    format_timestamp, print_success, print_error, print_info,
    console
)


@click.group()
def wallet():
    """Manage wallet balance and transactions"""
    pass


@wallet.command()
@click.pass_context
def balance(ctx):
    """
    Show wallet balance and status

    Examples:

      # Show wallet balance
      pdtrain wallet balance
    """
    config = ctx.obj['config']

    if not config.is_configured():
        print_error("CLI not configured. Run 'pdtrain configure' first.")
        ctx.exit(1)

    client = APIClient(config.api_url, config.api_key)

    try:
        balance_data = client.get_wallet_balance()

        # Create balance panel
        console.print("\n[bold cyan]═══ Wallet Balance ═══[/bold cyan]\n")

        # Create table for balance information
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Balance", f"${balance_data.get('balance_usd', 0):.2f}")
        table.add_row("Reserved", f"${balance_data.get('reserved_balance_usd', 0):.2f}")
        table.add_row("Available", f"[bold green]${balance_data.get('available_balance_usd', 0):.2f}[/bold green]")
        table.add_row("", "")
        table.add_row("Total Topped Up", f"${balance_data.get('total_topped_up_usd', 0):.2f}")
        table.add_row("Total Spent", f"${balance_data.get('total_spent_usd', 0):.2f}")

        console.print(table)

        # Low balance warning
        if balance_data.get('is_low_balance', False):
            threshold = balance_data.get('low_balance_threshold_usd', 10)
            console.print(f"\n[yellow]⚠ Warning: Balance is below ${threshold:.2f} threshold[/yellow]")

        # Auto top-up status
        if balance_data.get('auto_topup_enabled', False):
            auto_amount = balance_data.get('auto_topup_amount_usd', 50)
            console.print(f"\n[green]✓ Auto top-up enabled: ${auto_amount:.2f}[/green]")

        console.print()

    except Exception as e:
        print_error(f"Failed to get wallet balance: {str(e)}")
        ctx.exit(1)


@wallet.command()
@click.option('--limit', default=20, help='Number of transactions to show')
@click.option('--offset', default=0, help='Offset for pagination')
@click.pass_context
def transactions(ctx, limit, offset):
    """
    Show wallet transaction history

    Examples:

      # Show last 20 transactions
      pdtrain wallet transactions

      # Show last 50 transactions
      pdtrain wallet transactions --limit 50

      # Show next page
      pdtrain wallet transactions --limit 20 --offset 20
    """
    config = ctx.obj['config']

    if not config.is_configured():
        print_error("CLI not configured. Run 'pdtrain configure' first.")
        ctx.exit(1)

    client = APIClient(config.api_url, config.api_key)

    try:
        txs = client.get_wallet_transactions(limit=limit, offset=offset)

        if not txs:
            print_info("No transactions found")
            return

        console.print(f"\n[bold cyan]═══ Wallet Transactions (showing {len(txs)}) ═══[/bold cyan]\n")

        # Create table
        table = Table(show_header=True)
        table.add_column("Date", style="cyan", width=20)
        table.add_column("Type", style="yellow", width=10)
        table.add_column("Amount", style="white", width=12, justify="right")
        table.add_column("Balance", style="white", width=12, justify="right")
        table.add_column("Reference", style="magenta", width=20)
        table.add_column("Description", style="white", width=40)

        for tx in txs:
            tx_type = tx.get('transaction_type', 'unknown')
            amount = tx.get('amount_usd', 0)
            balance_after = tx.get('balance_after_usd', 0)
            reference_id = tx.get('reference_id', '-')
            description = tx.get('description', '-')
            created_at = tx.get('created_at', '')

            # Color code based on type
            if tx_type == 'topup':
                amount_str = f"[green]+${amount:.2f}[/green]"
            elif tx_type == 'charge':
                amount_str = f"[red]-${amount:.2f}[/red]"
            elif tx_type == 'refund':
                amount_str = f"[green]+${amount:.2f}[/green]"
            elif tx_type == 'hold':
                amount_str = f"[yellow]=${amount:.2f}[/yellow]"
            else:
                amount_str = f"${amount:.2f}"

            # Truncate reference and description
            if reference_id and len(reference_id) > 20:
                reference_id = reference_id[:17] + "..."
            if description and len(description) > 40:
                description = description[:37] + "..."

            table.add_row(
                format_timestamp(created_at),
                tx_type,
                amount_str,
                f"${balance_after:.2f}",
                reference_id or '-',
                description or '-'
            )

        console.print(table)
        console.print()

    except Exception as e:
        print_error(f"Failed to get transactions: {str(e)}")
        ctx.exit(1)


@wallet.command()
@click.option('--instance-type', required=True, help='Instance type (e.g., ml.m5.large)')
@click.option('--runtime', default=3600, help='Max runtime in seconds (default: 3600 = 1 hour)')
@click.option('--region', default='us-east-1', help='AWS region (default: us-east-1)')
@click.pass_context
def estimate(ctx, instance_type, runtime, region):
    """
    Estimate training job cost

    Examples:

      # Estimate cost for 1 hour on ml.m5.large
      pdtrain wallet estimate --instance-type ml.m5.large

      # Estimate cost for 2 hours on ml.g5.xlarge
      pdtrain wallet estimate --instance-type ml.g5.xlarge --runtime 7200

      # Estimate cost in us-west-2 region
      pdtrain wallet estimate --instance-type ml.p3.2xlarge --runtime 3600 --region us-west-2
    """
    config = ctx.obj['config']

    if not config.is_configured():
        print_error("CLI not configured. Run 'pdtrain configure' first.")
        ctx.exit(1)

    client = APIClient(config.api_url, config.api_key)

    try:
        estimate_data = client.estimate_job_cost(instance_type, runtime, region)

        console.print("\n[bold cyan]═══ Cost Estimate ═══[/bold cyan]\n")

        # Create table
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")

        # Runtime
        hours = runtime / 3600
        minutes = (runtime % 3600) / 60
        runtime_str = f"{int(hours)}h {int(minutes)}m" if hours >= 1 else f"{int(minutes)}m"

        table.add_row("Instance Type", instance_type)
        table.add_row("Region", region)
        table.add_row("Max Runtime", runtime_str)
        table.add_row("", "")
        table.add_row("Hourly Rate", f"${estimate_data.get('hourly_rate', 0):.4f}")
        table.add_row("Base Cost", f"${estimate_data.get('base_cost_usd', 0):.4f}")
        table.add_row("Safety Buffer (20%)", f"+${estimate_data.get('base_cost_usd', 0) * 0.2:.4f}")
        table.add_row("Estimated Cost", f"${estimate_data.get('estimated_cost_usd', 0):.4f}")
        table.add_row("", "")
        table.add_row("Platform Commission", f"${estimate_data.get('commission_amount_usd', 0):.4f}")
        table.add_row("", "")
        table.add_row("Total Cost", f"[bold green]${estimate_data.get('total_cost_usd', 0):.4f}[/bold green]")

        console.print(table)
        console.print()

        # Check wallet balance
        try:
            balance_data = client.get_wallet_balance()
            available = balance_data.get('available_balance_usd', 0)
            total_cost = estimate_data.get('total_cost_usd', 0)

            if available >= total_cost:
                console.print(f"[green]✓ Sufficient balance: ${available:.2f} available[/green]\n")
            else:
                console.print(f"[red]✗ Insufficient balance: ${available:.2f} available, ${total_cost:.2f} required[/red]\n")
                console.print(f"[yellow]  You need to add ${total_cost - available:.2f} to your wallet[/yellow]\n")
        except Exception:
            pass  # Ignore balance check errors

    except Exception as e:
        print_error(f"Failed to estimate cost: {str(e)}")
        ctx.exit(1)


@wallet.command()
@click.option('--instance-types', required=True, help='Comma-separated instance types to compare')
@click.option('--runtime', default=3600, help='Runtime in seconds (default: 3600 = 1 hour)')
@click.option('--region', default='us-east-1', help='AWS region (default: us-east-1)')
@click.pass_context
def compare(ctx, instance_types, runtime, region):
    """
    Compare costs across different instance types

    Examples:

      # Compare 3 instance types
      pdtrain wallet compare --instance-types ml.m5.large,ml.m5.xlarge,ml.m5.2xlarge

      # Compare GPU instances for 2 hours
      pdtrain wallet compare --instance-types ml.g5.xlarge,ml.g5.2xlarge,ml.p3.2xlarge --runtime 7200
    """
    config = ctx.obj['config']

    if not config.is_configured():
        print_error("CLI not configured. Run 'pdtrain configure' first.")
        ctx.exit(1)

    client = APIClient(config.api_url, config.api_key)

    try:
        instance_list = [t.strip() for t in instance_types.split(',')]
        comparison_data = client.compare_instance_costs(instance_list, runtime, region)

        # Runtime display
        hours = runtime / 3600
        minutes = (runtime % 3600) / 60
        runtime_str = f"{int(hours)}h {int(minutes)}m" if hours >= 1 else f"{int(minutes)}m"

        console.print(f"\n[bold cyan]═══ Instance Cost Comparison ({runtime_str}) ═══[/bold cyan]\n")

        # Create table
        table = Table(show_header=True)
        table.add_column("Instance Type", style="cyan", width=20)
        table.add_column("Hourly Rate", style="white", width=15, justify="right")
        table.add_column("Base Cost", style="white", width=15, justify="right")
        table.add_column("Total Cost", style="green", width=15, justify="right")
        table.add_column("vs Cheapest", style="yellow", width=15, justify="right")

        comparisons = comparison_data.get('comparisons', [])
        if not comparisons:
            print_error("No pricing data available for the specified instances")
            return

        # Find cheapest for comparison
        min_cost = min(c.get('total_cost_usd', float('inf')) for c in comparisons)

        for comp in comparisons:
            instance = comp.get('instance_type', 'unknown')
            hourly = comp.get('hourly_rate', 0)
            base = comp.get('base_cost_usd', 0)
            total = comp.get('total_cost_usd', 0)

            # Calculate difference from cheapest
            if total == min_cost:
                diff_str = "[green]CHEAPEST[/green]"
            else:
                diff_pct = ((total - min_cost) / min_cost * 100)
                diff_str = f"[yellow]+{diff_pct:.1f}%[/yellow]"

            table.add_row(
                instance,
                f"${hourly:.4f}",
                f"${base:.4f}",
                f"${total:.4f}",
                diff_str
            )

        console.print(table)
        console.print()

    except Exception as e:
        print_error(f"Failed to compare costs: {str(e)}")
        ctx.exit(1)


@wallet.command()
@click.option('--region', default='us-east-1', help='AWS region (default: us-east-1)')
@click.pass_context
def pricing(ctx, region):
    """
    Show available instance types and pricing

    Examples:

      # Show pricing for us-east-1
      pdtrain wallet pricing

      # Show pricing for us-west-2
      pdtrain wallet pricing --region us-west-2
    """
    config = ctx.obj['config']

    if not config.is_configured():
        print_error("CLI not configured. Run 'pdtrain configure' first.")
        ctx.exit(1)

    client = APIClient(config.api_url, config.api_key)

    try:
        pricing_data = client.get_instance_pricing(region)

        console.print(f"\n[bold cyan]═══ Instance Pricing ({region}) ═══[/bold cyan]\n")

        # Group by instance family
        instances_by_family = {}
        for instance_type, hourly_rate in pricing_data.get('pricing', {}).items():
            # Extract family (e.g., "ml.m5" from "ml.m5.large")
            parts = instance_type.split('.')
            if len(parts) >= 2:
                family = f"{parts[0]}.{parts[1]}"
                if family not in instances_by_family:
                    instances_by_family[family] = []
                instances_by_family[family].append((instance_type, hourly_rate))

        # Display by family
        for family in sorted(instances_by_family.keys()):
            instances = sorted(instances_by_family[family], key=lambda x: x[1])

            console.print(f"[bold yellow]{family}[/bold yellow]")

            table = Table(show_header=True, box=None, padding=(0, 2))
            table.add_column("Instance Type", style="cyan", width=20)
            table.add_column("Hourly Rate", style="white", width=15, justify="right")
            table.add_column("Daily (24h)", style="white", width=15, justify="right")
            table.add_column("Weekly (168h)", style="white", width=15, justify="right")

            for instance_type, hourly_rate in instances:
                daily = hourly_rate * 24
                weekly = hourly_rate * 168

                table.add_row(
                    instance_type,
                    f"${hourly_rate:.4f}",
                    f"${daily:.2f}",
                    f"${weekly:.2f}"
                )

            console.print(table)
            console.print()

    except Exception as e:
        print_error(f"Failed to get pricing: {str(e)}")
        ctx.exit(1)
