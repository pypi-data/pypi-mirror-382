# pdtrain CLI Complete Guide

Complete command reference for the Pipedream Training Orchestrator CLI.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Wallet Commands](#wallet-commands) ⭐ **NEW - Manage balance & costs**
- [Pipeline Commands](#pipeline-commands) ⭐ **NEW - All-in-one command**
- [Template Commands](#template-commands)
- [Bundle Commands](#bundle-commands)
- [Dataset Commands](#dataset-commands)
- [Run Commands](#run-commands)
- [Logs Commands](#logs-commands)
- [Artifacts Commands](#artifacts-commands)
- [Quota Commands](#quota-commands)
- [Complete Workflow Example](#complete-workflow-example)

## Installation

```bash
# Install from source (development)
git clone https://github.com/pipedream/pdtrain
cd pdtrain
pip install -e .

# Verify installation
pdtrain --version
```

## Configuration

### Initial Setup

```bash
pdtrain configure
```

You'll be prompted for:
- **API URL**: `http://localhost:8000` (or your production URL)
- **API Key**: `sdk_xxxxx` (from Pipedream dashboard)

### Environment Variables

Alternatively, use environment variables:

```bash
export PDTRAIN_API_URL=https://orchestrator.pipedream.ai
export PDTRAIN_API_KEY=sdk_xxxxx
```

### View Configuration

```bash
pdtrain info
```

---

## Wallet Commands

⭐ **NEW:** Manage your wallet balance, view transactions, and estimate training costs before running jobs!

### Check Wallet Balance

View your current wallet balance and transaction limits.

```bash
pdtrain wallet balance
```

**Output:**
```
═══ Wallet Balance ═══

Balance        $100.00
Reserved       $5.00
Available      $95.00

Total Topped Up  $100.00
Total Spent      $5.00

✓ Auto top-up enabled: $50.00
```

### View Transaction History

List your wallet transaction history with pagination.

```bash
pdtrain wallet transactions

# Show last 50 transactions
pdtrain wallet transactions --limit 50

# Pagination
pdtrain wallet transactions --limit 20 --offset 20
```

**Output:**
```
═══ Wallet Transactions (showing 10) ═══

Date                  Type      Amount       Balance      Reference              Description
2025-01-15 14:30:25   topup     +$100.00     $100.00      -                      Initial wallet funding
2025-01-15 14:35:12   hold      =$5.50       $100.00      run-20250115143512     Reserved $5.50 for training job
2025-01-15 15:20:45   charge    -$4.75       $95.25       run-20250115143512     Charged $4.75 for training job
2025-01-15 15:20:46   refund    +$0.75       $96.00       run-20250115143512     Refunded $0.75 unused funds
```

**Transaction Types:**
- `topup` - Funds added to wallet
- `hold` - Funds reserved for estimated job cost
- `charge` - Actual cost charged after job completes
- `refund` - Unused funds returned to wallet

### Estimate Job Cost

Estimate the cost of a training job before creating it.

```bash
# Estimate cost for 1 hour on ml.m5.large
pdtrain wallet estimate --instance-type ml.m5.large

# Estimate cost for 2 hours on GPU instance
pdtrain wallet estimate --instance-type ml.g5.xlarge --runtime 7200

# Estimate in different region
pdtrain wallet estimate \
  --instance-type ml.p3.2xlarge \
  --runtime 3600 \
  --region us-west-2
```

**Output:**
```
═══ Cost Estimate ═══

Instance Type      ml.g5.xlarge
Region             us-east-1
Max Runtime        2h 0m

Hourly Rate        $1.0060
Base Cost          $2.0120
Safety Buffer (20%)  +$0.4024
Estimated Cost     $2.4144

Platform Commission  $0.2414

Total Cost         $2.6558

✓ Sufficient balance: $95.00 available
```

**What's included:**
- **Base Cost**: Instance hourly rate × runtime
- **Safety Buffer**: 20% overestimate to cover variations
- **Platform Commission**: Platform fee (default: 10%)
- **Total Cost**: Amount that will be reserved from your wallet

### Compare Instance Costs

Compare costs across different instance types to find the best value.

```bash
# Compare general purpose instances
pdtrain wallet compare \
  --instance-types ml.m5.large,ml.m5.xlarge,ml.m5.2xlarge

# Compare GPU instances for 2 hours
pdtrain wallet compare \
  --instance-types ml.g5.xlarge,ml.g5.2xlarge,ml.p3.2xlarge \
  --runtime 7200

# Compare in different region
pdtrain wallet compare \
  --instance-types ml.m5.large,ml.m6i.large,ml.m7i.large \
  --runtime 3600 \
  --region us-west-2
```

**Output:**
```
═══ Instance Cost Comparison (2h 0m) ═══

Instance Type          Hourly Rate     Base Cost       Total Cost      vs Cheapest
ml.g5.xlarge          $1.0060         $2.0120         $2.6558         CHEAPEST
ml.g5.2xlarge         $1.2120         $2.4240         $3.1997         +20.5%
ml.p3.2xlarge         $3.0600         $6.1200         $8.0784         +204.2%
```

### View Instance Pricing

Show all available instance types and their pricing for a region.

```bash
# Show pricing for us-east-1
pdtrain wallet pricing

# Show pricing for us-west-2
pdtrain wallet pricing --region us-west-2
```

**Output:**
```
═══ Instance Pricing (us-east-1) ═══

ml.m5
  Instance Type        Hourly Rate     Daily (24h)     Weekly (168h)
  ml.m5.large         $0.1150         $2.76           $19.32
  ml.m5.xlarge        $0.2300         $5.52           $38.64
  ml.m5.2xlarge       $0.4600         $11.04          $77.28
  ml.m5.4xlarge       $0.9220         $22.13          $154.90

ml.g5
  Instance Type        Hourly Rate     Daily (24h)     Weekly (168h)
  ml.g5.xlarge        $1.0060         $24.14          $168.96
  ml.g5.2xlarge       $1.2120         $29.09          $203.62
  ml.g5.4xlarge       $2.1760         $52.22          $365.57

ml.p3
  Instance Type        Hourly Rate     Daily (24h)     Weekly (168h)
  ml.p3.2xlarge       $3.0600         $73.44          $514.08
  ml.p3.8xlarge       $12.2400        $293.76         $2,056.32
```

**Cost Planning Tips:**
1. **Check wallet balance before submitting** - Estimate cost first to ensure sufficient funds
2. **Use cost comparison** - Find the cheapest instance that meets your needs
3. **Monitor your balance** - Set up auto top-up to avoid job termination
4. **Review transactions** - Check your spending history regularly

---

## Pipeline Commands

⭐ **NEW:** All-in-one command that combines all steps into a single workflow!

### Run Complete Pipeline

Execute the entire training pipeline in one command: upload bundle, upload dataset, create run, and submit to SageMaker.

```bash
pdtrain pipeline run [OPTIONS]
```

**Required Options:**
- `--bundle-path PATH` - Path to training code (directory or .tar.gz file)

**Dataset Options:**
- `--dataset-path PATH` - Path to dataset (file or directory)
- `--dataset-name TEXT` - Dataset name (required if dataset-path provided)

**Framework Options:**
- `--framework TEXT` - Framework (pytorch, tensorflow, sklearn, xgboost, huggingface)
- `--framework-version TEXT` - Framework version (e.g., 2.2.0)
- `--python-version TEXT` - Python version (e.g., py310)
- `--image TEXT` - Docker image URI (for custom container mode)

**Training Options:**
- `--entry TEXT` - Entry point script (default: train.py)
- `--env TEXT` - Environment variable KEY=VALUE (can specify multiple)
- `--hyperparameter TEXT` - Hyperparameter KEY=VALUE (can specify multiple)
- `--spot` - Use spot instances (70% cost savings)
- `--wait` - Wait for training completion

**Advanced Options:**
- `--bundle-name TEXT` - Bundle name (defaults to directory/file name)
- `--bundle-exclude PATTERN` - Exclude bundle files (can specify multiple)
- `--dataset-exclude PATTERN` - Exclude dataset files (can specify multiple)

**What it does:**
1. ✅ Uploads your training code bundle
2. ✅ Uploads your dataset (if provided)
3. ✅ Creates a training run with your configuration
4. ✅ Submits the run to SageMaker
5. ✅ (Optional) Waits for completion with `--wait`

**Examples:**

```bash
# Minimal pipeline - just code and PyTorch
pdtrain pipeline run \
  --bundle-path ./my-training-code \
  --framework pytorch

# Full pipeline with dataset and hyperparameters
pdtrain pipeline run \
  --bundle-path ./my-code \
  --dataset-path ./data.csv \
  --dataset-name "train-data" \
  --framework pytorch \
  --framework-version 2.2.0 \
  --hyperparameter epochs=100 \
  --hyperparameter batch_size=64 \
  --hyperparameter learning_rate=0.001

# Pipeline with directory dataset and environment variables
pdtrain pipeline run \
  --bundle-path ./training \
  --dataset-path ./image-dataset \
  --dataset-name "cifar10" \
  --framework pytorch \
  --framework-version 2.2.0 \
  --python-version py310 \
  --env WANDB_API_KEY=xxxxx \
  --env CUDA_VISIBLE_DEVICES=0,1 \
  --hyperparameter epochs=50

# Pipeline with spot instances and wait for completion
pdtrain pipeline run \
  --bundle-path ./my-code \
  --dataset-path ./data.parquet \
  --dataset-name "training-set" \
  --framework tensorflow \
  --framework-version 2.13.0 \
  --spot \
  --wait

# Custom Docker image pipeline
pdtrain pipeline run \
  --bundle-path ./my-code \
  --image 763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-training:2.2.0-gpu \
  --env MY_CONFIG=production \
  --hyperparameter batch_size=128

# Pipeline with exclusions
pdtrain pipeline run \
  --bundle-path ./training \
  --bundle-exclude "*.log" \
  --bundle-exclude "checkpoints" \
  --dataset-path ./data-dir \
  --dataset-name "my-dataset" \
  --dataset-exclude "*.tmp" \
  --dataset-exclude "raw" \
  --framework pytorch
```

**Output:**

The pipeline command provides clear step-by-step progress:

```
═══ Training Pipeline ═══

Step 1/4: Upload Bundle
Creating tar.gz from directory my-training-code...
✓ Created my-training-code.tar.gz (12.5 KB)
✓ Quota check passed (4.9 GB available)
Uploading my-training-code.tar.gz (12.5 KB)...
✓ Upload complete
Waiting for validation...
✓ Validation passed
✓ Bundle uploaded: ca8912d6-79a4-4ea9-8570-234ec1baeef1

Step 2/4: Upload Dataset
Creating tar.gz from directory data...
✓ Created train-data.tar.gz (2.3 MB)
✓ Quota check passed (9.8 GB available)
Uploading train-data.tar.gz (2.3 MB)...
✓ Upload complete
Waiting for validation...
✓ Validation passed
✓ Dataset uploaded: ds_abc123-def456-7890

Step 3/4: Create Training Run
Status: created
Framework: pytorch 2.2.0
Instance: ml.g4dn.xlarge
✓ Run created: run-20251006123456

Step 4/4: Submit to SageMaker
Submitting to SageMaker...
Waiting for job ARN...
✓ Job ARN: arn:aws:sagemaker:us-east-1:...
✓ Run submitted successfully

═══ Pipeline Complete ═══

Run ID: run-20251006123456
Bundle ID: ca8912d6-79a4-4ea9-8570-234ec1baeef1
Dataset ID: ds_abc123-def456-7890

Next steps:
  • View logs: pdtrain logs run-20251006123456 --follow
  • Check status: pdtrain run show run-20251006123456
  • Download artifacts: pdtrain artifacts download run-20251006123456
```

**Benefits vs. Individual Commands:**

| Individual Commands | Pipeline Command |
|-------------------|-----------------|
| 4-5 separate commands | 1 single command |
| Manual ID copying | Automatic ID handling |
| Multiple steps to track | Clear progress display |
| More room for errors | Streamlined workflow |

**When to use:**
- ✅ Quick iterations during development
- ✅ Simple training workflows
- ✅ When you want minimal command complexity
- ✅ Automated scripts/CI-CD pipelines

**When to use individual commands:**
- Use existing bundles/datasets with new configurations
- Need fine-grained control over each step
- Debugging specific upload or creation issues
- Reusing previously uploaded artifacts

---

## Template Commands

### List Available Frameworks

Show all supported frameworks, versions, and Python versions:

```bash
pdtrain template frameworks
```

**Output:**
```
Available Frameworks

● pytorch - PyTorch deep learning framework
  Versions: 2.2.0, 2.1.0, 2.0.1, 1.13.1
  Python: py310, py39, py38

● tensorflow - TensorFlow deep learning framework
  Versions: 2.13.0, 2.12.0, 2.11.0, 2.10.0
  Python: py310, py39, py38

...
```

### Generate Run Config Template

Generate a YAML configuration template with all options:

```bash
pdtrain template run [--output FILE]
```

**Example:**
```bash
# Generate default pdtrain-config.yaml
pdtrain template run

# Custom output file
pdtrain template run --output my-config.yaml
```

This creates a complete template showing all available options, framework versions, and examples.

---

## Bundle Commands

### Upload Bundle

Upload training code as a directory (auto-creates tar.gz) or existing tar.gz file.

```bash
pdtrain bundle upload <path> [OPTIONS]
```

**Supported inputs:**
- Directory (automatically creates tar.gz)
- `.tar.gz` or `.tgz` file

**Options:**
- `--name TEXT` - Bundle name (defaults to directory/file name)
- `--exclude PATTERN` - Exclude files/patterns (can specify multiple)
- `--wait` - Wait for validation to complete

**Features:**
- ✅ Automatic quota check before upload
- ✅ Auto-creates tar.gz from directories
- ✅ Automatic exclusion of common unnecessary files (`.git`, `__pycache__`, `*.pyc`, `.venv`, etc.)
- ✅ Custom exclusion patterns via `--exclude`
- ✅ Validates bundle structure
- ✅ Shows validation results

**Default Exclusions:**
The following patterns are automatically excluded:
- `__pycache__`, `*.pyc`, `*.pyo`, `*.pyd`
- `.git`, `.gitignore`, `.DS_Store`
- `.venv`, `venv`, `.env`
- `*.egg-info`, `dist`, `build`
- `.pytest_cache`, `.Python`, `*.so`

**Examples:**

```bash
# Upload directory (automatically creates tar.gz)
pdtrain bundle upload ./my-training-code --wait

# Upload directory with custom name
pdtrain bundle upload ./src --name "resnet-training" --wait

# Upload with additional exclusions
pdtrain bundle upload ./my-code \
  --exclude "*.log" \
  --exclude "data" \
  --exclude "checkpoints" \
  --wait

# Upload existing tar.gz file
pdtrain bundle upload ./code.tar.gz --wait
```

### List Bundles

List all uploaded bundles with full IDs.

```bash
pdtrain bundle list
```

**Output format:**
```
================================================================================
ID: ca8912d6-79a4-4ea9-8570-234ec1baeef1
Name: pytorch-image-classification:v1.0.0  Status: ready  Size: 6.2 KB  Created: 30 minutes ago
--------------------------------------------------------------------------------
```

IDs are shown in full for easy copying.

### Show Bundle Details

Display detailed information about a bundle.

```bash
pdtrain bundle show <bundle_id>
```

**Example:**
```bash
pdtrain bundle show ca8912d6-79a4-4ea9-8570-234ec1baeef1
```

---

## Dataset Commands

### Upload Dataset

Upload a dataset (file or directory).

```bash
pdtrain dataset upload <path> [OPTIONS]
```

**Supported formats:**
- **Files**: `.csv`, `.parquet`, `.json`, `.jsonl`, `.zip`, `.tar.gz`, `.tgz`
- **Directories**: Automatically creates tar.gz

**Options:**
- `--name TEXT` - Dataset name (required)
- `--description TEXT` - Dataset description
- `--exclude PATTERN` - Exclude files/patterns (can specify multiple)
- `--wait` - Wait for validation

**Features:**
- ✅ Automatic quota check before upload
- ✅ Auto-creates tar.gz from directories
- ✅ Automatic exclusion of common unnecessary files (`.DS_Store`, `.git`, `*.tmp`, etc.)
- ✅ Custom exclusion patterns via `--exclude`
- ✅ Validates file format
- ✅ Shows metadata (rows, columns, file type)

**Default Exclusions:**
The following patterns are automatically excluded:
- `.DS_Store`, `Thumbs.db`
- `.git`, `.gitignore`
- `__MACOSX`
- `*.tmp`, `*.cache`

**Examples:**

```bash
# Upload CSV file
pdtrain dataset upload ./data.csv --name "train-data" --wait

# Upload directory (automatically creates tar.gz)
pdtrain dataset upload ./image-dataset --name "cifar10" --wait

# Upload with description
pdtrain dataset upload ./cifar10.parquet \
  --name "cifar10" \
  --description "CIFAR-10 training dataset" \
  --wait

# Upload image dataset with exclusions
pdtrain dataset upload ./my-images \
  --name "image-classification" \
  --exclude "*.DS_Store" \
  --exclude "*.tmp" \
  --exclude "raw" \
  --wait
```

### List Datasets

List all datasets with full IDs.

```bash
pdtrain dataset list [OPTIONS]
```

**Options:**
- `--limit INTEGER` - Number of datasets to show (default: 50)
- `--name TEXT` - Filter by name

**Output format:**
```
================================================================================
ID: ds_abc123-def456-7890
Name: train-data:v1  Visibility: private  Created: 1 minute ago
--------------------------------------------------------------------------------
```

**Example:**
```bash
pdtrain dataset list --name "cifar"
```

### Show Dataset Details

Display detailed information about a dataset.

```bash
pdtrain dataset show <dataset_id>
```

**Example:**
```bash
pdtrain dataset show ds_abc123-def456-7890
```

### Download Dataset

Download a dataset.

```bash
pdtrain dataset download <dataset_id> [OPTIONS]
```

**Options:**
- `--version INTEGER` - Dataset version (default: 1)
- `--output PATH` - Output directory (default: current directory)

**Example:**
```bash
pdtrain dataset download ds_abc123 --output ./data/
```

### Delete Dataset

Delete a dataset (all versions).

```bash
pdtrain dataset delete <dataset_id>
```

Requires confirmation prompt.

**Example:**
```bash
pdtrain dataset delete ds_abc123
```

---

## Run Commands

### Create Run

Create a new training run using bundle and dataset IDs.

```bash
pdtrain run create [OPTIONS]
```

**Required Options:**
- `--bundle TEXT` - Bundle ID (from `pdtrain bundle list`)

**Framework Mode Options:**
- `--framework TEXT` - Framework (pytorch, tensorflow, sklearn, xgboost, huggingface)
- `--framework-version TEXT` - Framework version (e.g., 2.2.0)
- `--python-version TEXT` - Python version (e.g., py310)

**Docker Mode Options:**
- `--image TEXT` - Docker image URI (for custom container mode)

**General Options:**
- `--dataset TEXT` - Dataset ID (from `pdtrain dataset list`) - can specify multiple
- `--entry TEXT` - Entry point script (default: train.py)
- `--env TEXT` - Environment variable KEY=VALUE (can specify multiple)
- `--hyperparameter TEXT` - Hyperparameter KEY=VALUE (can specify multiple)
- `--spot` - Use spot instances (70% cost savings)
- `--submit` - Submit immediately after creation
- `--wait` - Wait for completion (implies --submit)

**Important:** Use IDs from `pdtrain bundle list` and `pdtrain dataset list`, not names!

**Examples:**

```bash
# Get IDs first
pdtrain bundle list      # Copy bundle ID
pdtrain dataset list     # Copy dataset ID

# Basic run with framework mode
pdtrain run create \
  --bundle ca8912d6-79a4-4ea9-8570-234ec1baeef1 \
  --framework pytorch

# Run with dataset and hyperparameters
pdtrain run create \
  --bundle ca8912d6-79a4-4ea9-8570-234ec1baeef1 \
  --dataset ds_abc123-def456-7890 \
  --framework pytorch \
  --framework-version 2.2.0 \
  --hyperparameter epochs=50 \
  --hyperparameter batch_size=64 \
  --submit --wait

# Docker mode with custom image
pdtrain run create \
  --bundle ca8912d6-79a4-4ea9-8570-234ec1baeef1 \
  --image 763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-training:2.2.0-gpu \
  --env CUDA_VISIBLE_DEVICES=0,1 \
  --submit

# Multiple datasets with spot instances
pdtrain run create \
  --bundle ca8912d6-79a4-4ea9-8570-234ec1baeef1 \
  --dataset ds_train123 \
  --dataset ds_val456 \
  --framework pytorch \
  --hyperparameter learning_rate=0.001 \
  --spot \
  --submit
```

### Other Run Commands

```bash
# Submit a pending run
pdtrain run submit <run_id>

# List all runs
pdtrain run list [--limit N] [--status STATUS]

# Show run details
pdtrain run show <run_id>

# Watch run progress in real-time
pdtrain run watch <run_id> [--interval SECONDS]

# Stop a running job
pdtrain run stop <run_id>

# Refresh status from SageMaker
pdtrain run refresh <run_id>
```

---

## Logs Commands

### View Logs

View training logs for a run.

```bash
pdtrain logs <run_id> [OPTIONS]
```

**Options:**
- `--lines INTEGER` - Number of lines to show (default: 300)
- `--follow` - Follow logs in real-time
- `--interval INTEGER` - Polling interval for --follow in seconds (default: 5)

**Examples:**

```bash
# View last 500 lines
pdtrain logs run-20251002091335 --lines 500

# Follow logs in real-time
pdtrain logs run-20251002091335 --follow --interval 3
```

Press `Ctrl+C` to stop following logs.

---

## Artifacts Commands

### List Artifacts

List all artifacts for a run.

```bash
pdtrain artifacts list <run_id>
```

**Example:**
```bash
pdtrain artifacts list run-20251002091335
```

### Download Artifacts

Download all artifacts from a run.

```bash
pdtrain artifacts download <run_id> [OPTIONS]
```

**Options:**
- `--output PATH` - Output directory (default: `./artifacts/<run_id>/`)

**Examples:**

```bash
# Download to default location
pdtrain artifacts download run-20251002091335

# Download to specific directory
pdtrain artifacts download run-20251002091335 --output ./results/
```

---

## Quota Commands

### Check Storage Quota

View current storage quota usage.

```bash
pdtrain quota
```

**Output:**
```
╭─────────────────────────────────────────────╮
│ Storage Quota                               │
│                                             │
│ Datasets: 0 B / 10.0 GB (0.0%)             │
│ Bundles: 6.2 KB / 5.0 GB (0.0%)            │
│                                             │
│ Dataset Count: 0 / 5                       │
│ Bundle Count: 1                            │
│                                             │
│ Limits:                                     │
│ Max Dataset Size: 1 GB                     │
│ Max Bundle Size: 500 MB                    │
│ Dataset Retention: 30 days                 │
╰─────────────────────────────────────────────╯
```

**Features:**
- ✅ Shows storage usage for bundles and datasets separately
- ✅ Display count limits
- ✅ Shows max file sizes
- ✅ Warns when usage > 80%

---

## Complete Workflow Example

### Option 1: Pipeline Command (Recommended - Simple & Fast) ⭐

The fastest way to get started - all steps in one command:

```bash
# 1. Configure CLI (first time only)
pdtrain configure

# 2. Run complete pipeline in ONE command
pdtrain pipeline run \
  --bundle-path ./my-training-code \
  --dataset-path ./data.csv \
  --dataset-name "train-data" \
  --framework pytorch \
  --framework-version 2.2.0 \
  --python-version py310 \
  --hyperparameter epochs=100 \
  --hyperparameter batch_size=128 \
  --env WANDB_API_KEY=xxxxx

# 3. View logs (use run_id from step 2 output)
pdtrain logs <run-id> --follow

# 4. Download results when complete
pdtrain artifacts download <run-id> --output ./results/
```

### Option 2: Individual Commands (Advanced - More Control)

For fine-grained control or reusing existing artifacts:

```bash
# 1. Check available frameworks (optional)
pdtrain template frameworks

# 2. Configure CLI (first time only)
pdtrain configure

# 3. Upload training code from directory
pdtrain bundle upload ./my-training-code --wait

# 4. Upload dataset
pdtrain dataset upload ./data.csv --name "train-data" --wait

# 5. Get IDs
pdtrain bundle list      # Copy the bundle ID
pdtrain dataset list     # Copy the dataset ID

# 6. Create and run training
pdtrain run create \
  --bundle <bundle-id-from-step-5> \
  --dataset <dataset-id-from-step-5> \
  --framework pytorch \
  --framework-version 2.2.0 \
  --python-version py310 \
  --entry train.py \
  --hyperparameter epochs=100 \
  --hyperparameter batch_size=128 \
  --env WANDB_API_KEY=xxxxx \
  --submit

# 7. Watch progress (get run_id from step 6)
pdtrain run watch <run-id>

# 8. View logs
pdtrain logs <run-id> --follow

# 9. Download results when complete
pdtrain artifacts download <run-id> --output ./results/

# 10. Check quota usage
pdtrain quota
```

**Which option should you use?**

- 🚀 **Use Pipeline Command** if: First time user, simple workflow, want speed, scripting/CI-CD
- 🔧 **Use Individual Commands** if: Reusing bundles/datasets, need fine-grained control, debugging

---

## Key Changes from Previous Versions

### ID-Based References (v0.1.0+)

**Before:**
```bash
pdtrain run create --bundle my-model:latest --dataset cifar10:1
```

**Now:**
```bash
# Get IDs first
pdtrain bundle list
pdtrain dataset list

# Use IDs
pdtrain run create --bundle <bundle-id> --dataset <dataset-id>
```

### Directory Upload Support

Both bundles and datasets now support directory uploads:

```bash
# Automatically creates tar.gz
pdtrain bundle upload ./my-code --wait
pdtrain dataset upload ./my-data --name "dataset-name" --wait
```

### Quota Checking

Uploads now check quota **before** uploading to prevent wasted bandwidth:

```bash
⠼ Checking storage quota...
✓ Quota check passed (4.9 GB bundle storage available)
```

### Template System

New template commands help avoid framework/version errors:

```bash
pdtrain template frameworks  # See available frameworks
pdtrain template run         # Generate config template
```

---

## Tips & Best Practices

### Getting IDs

Always use `list` commands to get IDs:
```bash
pdtrain bundle list | grep "my-bundle"
pdtrain dataset list | grep "my-data"
```

Then copy the full ID from the output.

### Framework Versions

Use `pdtrain template frameworks` to see available versions before creating runs.

### Quota Management

- Check quota regularly: `pdtrain quota`
- Delete old bundles/datasets to free space
- Use spot instances (`--spot`) for 70% cost savings

### Spot Instances

- Use `--spot` flag for fault-tolerant workloads
- 70% cost savings vs on-demand
- May be interrupted by AWS

### Run Monitoring

- Use `--wait` to block until completion
- Use `--follow` on logs for real-time monitoring
- Use `run watch` for status updates without logs

---

## Troubleshooting

### Command not found: pdtrain

```bash
# Upgrade pip and setuptools first
pip install --upgrade pip setuptools

# Then install
pip install -e .
```

### CLI not configured

```bash
pdtrain configure
```

### Connection refused

```bash
# Verify API is running
curl http://localhost:8000/health
```

### Insufficient quota

```bash
# Check usage
pdtrain quota

# Delete old data
pdtrain bundle list
pdtrain bundle delete <id>

pdtrain dataset list
pdtrain dataset delete <id>
```

### Invalid bundle/dataset ID

Make sure you're copying the full ID from `list` commands, not the name.

---

## Getting Help

```bash
# General help
pdtrain --help

# Command-specific help
pdtrain bundle --help
pdtrain run create --help
pdtrain template --help
```
