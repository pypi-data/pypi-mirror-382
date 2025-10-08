"""Main CLI entry point for pdtrain"""

import click
from rich.console import Console

from pdtrain import __version__
from pdtrain.config import get_config, Config
from pdtrain.utils.formatters import print_error, print_success, print_info
from pdtrain.commands import bundle, dataset, run, logs, artifacts, quota, template, pipeline, wallet, plan


console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="pdtrain")
@click.pass_context
def cli(ctx):
    """
    pdtrain - Pipedream Training Orchestrator CLI

    Train ML models on AWS SageMaker with ease.
    """
    ctx.ensure_object(dict)
    ctx.obj['config'] = get_config()


@cli.command()
def configure():
    """Configure pdtrain CLI"""
    console.print("\n[bold cyan]pdtrain Configuration[/bold cyan]\n")

    # Get API URL
    current_url = get_config().api_url or "http://localhost:8000"
    api_url = click.prompt(
        "API URL",
        default=current_url,
        type=str
    )

    # Get API Key
    current_key = get_config().api_key
    if current_key:
        api_key = click.prompt(
            "API Key",
            default="<current>",
            type=str,
            hide_input=True
        )
        if api_key == "<current>":
            api_key = current_key
    else:
        api_key = click.prompt(
            "API Key",
            type=str,
            hide_input=True
        )

    # Save configuration
    config = Config(api_url=api_url, api_key=api_key)
    config.save()

    print_success(f"Configuration saved to {Config.get_config_path()}")
    print_info(f"API URL: {api_url}")


@cli.command()
@click.pass_context
def info(ctx):
    """Show configuration and API information"""
    config = ctx.obj['config']

    console.print("\n[bold cyan]pdtrain Information[/bold cyan]\n")
    console.print(f"Version: {__version__}")
    console.print(f"Config: {Config.get_config_path()}")
    console.print(f"API URL: {config.api_url}")

    if config.api_key:
        console.print(f"API Key: {config.api_key[:10]}...")
        console.print(f"Configured: [green]Yes[/green]")
    else:
        console.print(f"API Key: [red]Not configured[/red]")
        console.print(f"Configured: [red]No[/red]")
        console.print("\nRun [cyan]pdtrain configure[/cyan] to set up your API key")


# Register command groups
cli.add_command(bundle.bundle)
cli.add_command(dataset.dataset)
cli.add_command(run.run)
cli.add_command(logs.logs)
cli.add_command(artifacts.artifacts)
cli.add_command(quota.quota)
cli.add_command(template.template)
cli.add_command(pipeline.pipeline)
cli.add_command(wallet.wallet)
cli.add_command(plan.plan)


def main():
    """Main entry point"""
    cli(obj={})


if __name__ == "__main__":
    main()
