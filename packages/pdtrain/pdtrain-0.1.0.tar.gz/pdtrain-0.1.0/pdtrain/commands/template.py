"""Template and config generation commands"""

import click
import yaml
from pathlib import Path
from pdtrain.utils.formatters import print_success, print_error, print_info, console
from rich.table import Table


@click.group()
def template():
    """Generate configuration templates"""
    pass


@template.command()
@click.option('--output', type=click.Path(), help='Output file (default: pdtrain-config.yaml)')
@click.pass_context
def run(ctx, output):
    """Generate a training run configuration template"""

    output_path = Path(output) if output else Path.cwd() / 'pdtrain-config.yaml'

    # Template configuration with all options and examples
    config = {
        'run': {
            'bundle_id': '<your-bundle-id>  # Get from: pdtrain bundle list',
            'entry': 'train.py',
            'datasets': [
                '<dataset-id-1>  # Get from: pdtrain dataset list',
                '<dataset-id-2>  # Optional: add multiple datasets'
            ],
            'framework': {
                'name': 'pytorch',  # Options: pytorch, tensorflow, sklearn, xgboost, huggingface
                'version': '2.2.0',  # Framework version
                'python_version': 'py310'  # Options: py38, py39, py310, py311
            },
            'hyperparameters': {
                'epochs': 100,
                'batch_size': 64,
                'learning_rate': 0.001,
                'optimizer': 'adam'
            },
            'environment': {
                'WANDB_API_KEY': 'your-wandb-key',
                'DATA_DIR': '/opt/ml/input/data',
                'OUTPUT_DIR': '/opt/ml/output'
            },
            'compute': {
                'spot_instances': False  # Set to true for 70% cost savings
            }
        },
        'examples': {
            'pytorch': {
                'framework': 'pytorch',
                'versions': ['2.2.0', '2.1.0', '2.0.1', '1.13.1'],
                'python_versions': ['py310', 'py39', 'py38']
            },
            'tensorflow': {
                'framework': 'tensorflow',
                'versions': ['2.13.0', '2.12.0', '2.11.0'],
                'python_versions': ['py310', 'py39', 'py38']
            },
            'sklearn': {
                'framework': 'sklearn',
                'versions': ['1.3.0', '1.2.2'],
                'python_versions': ['py310', 'py39']
            },
            'xgboost': {
                'framework': 'xgboost',
                'versions': ['1.7.0', '1.6.0'],
                'python_versions': ['py310', 'py39']
            },
            'huggingface': {
                'framework': 'huggingface',
                'versions': ['4.28.0', '4.26.0'],
                'python_versions': ['py310', 'py39']
            }
        }
    }

    try:
        # Write YAML file
        with open(output_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        print_success(f"Generated config template: {output_path}")
        print_info("\nNext steps:")
        print_info("1. Edit the config file with your bundle/dataset IDs")
        print_info("2. Run: pdtrain run create --config pdtrain-config.yaml")

    except Exception as e:
        print_error(f"Failed to generate template: {str(e)}")
        ctx.exit(1)


@template.command()
@click.pass_context
def frameworks(ctx):
    """List available frameworks and versions"""

    frameworks_info = {
        'pytorch': {
            'versions': ['2.2.0', '2.1.0', '2.0.1', '1.13.1'],
            'python': ['py310', 'py39', 'py38'],
            'description': 'PyTorch deep learning framework'
        },
        'tensorflow': {
            'versions': ['2.13.0', '2.12.0', '2.11.0', '2.10.0'],
            'python': ['py310', 'py39', 'py38'],
            'description': 'TensorFlow deep learning framework'
        },
        'sklearn': {
            'versions': ['1.3.0', '1.2.2', '1.2.0'],
            'python': ['py310', 'py39', 'py38'],
            'description': 'Scikit-learn machine learning'
        },
        'xgboost': {
            'versions': ['1.7.0', '1.6.0', '1.5.0'],
            'python': ['py310', 'py39', 'py38'],
            'description': 'XGBoost gradient boosting'
        },
        'huggingface': {
            'versions': ['4.28.0', '4.26.0', '4.24.0'],
            'python': ['py310', 'py39', 'py38'],
            'description': 'Hugging Face Transformers'
        }
    }

    console.print("\n[bold cyan]Available Frameworks[/bold cyan]\n")

    for fw, info in frameworks_info.items():
        console.print(f"[green]●[/green] [bold]{fw}[/bold] - {info['description']}")
        console.print(f"  Versions: {', '.join(info['versions'])}")
        console.print(f"  Python: {', '.join(info['python'])}\n")

    console.print("[bold]Examples:[/bold]")
    console.print("  pdtrain run create --bundle <id> --framework pytorch --framework-version 2.2.0")
    console.print("  pdtrain run create --bundle <id> --framework tensorflow --framework-version 2.13.0")
    console.print("\nOr generate a config template:")
    console.print("  pdtrain template run")
