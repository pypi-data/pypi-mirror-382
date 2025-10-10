# 🚀 DAGnostics MLOps Setup Guide

Your DAGnostics project now includes production-grade MLOps capabilities! This guide will help you set up and use the new MLOps features.

## ✨ What's New

DAGnostics now includes a comprehensive MLOps system that transforms your training pipeline into a production-ready ML operations platform:

### 🎯 Core MLOps Features
- **Experiment Tracking** with MLflow and Weights & Biases
- **Data Validation** and quality assessment
- **Hyperparameter Optimization** with Optuna
- **Model Versioning** and registry
- **Pipeline Monitoring** and logging
- **Data Drift Detection**
- **Automated Model Validation**

### 🔄 Integration with Your Current Workflow

Your existing remote training command now supports MLOps features:

```bash
# Your current workflow (still works!)
uv run dagnostics training remote-train --server-url http://172.16.5.60:8001 --epochs 1

# Enhanced with MLOps (new!)
uv run dagnostics training remote-train --server-url http://172.16.5.60:8001 --epochs 3 --enable-mlops --enable-hpo
```

## 🛠️ Setup Instructions

### 1. Install MLOps Dependencies

```bash
# Quick setup
python install_mlops.py

# Manual installation
pip install -r mlops/requirements.txt
```

### 2. Verify Setup

```bash
# Check MLOps system status
uv run python -m mlops.cli status

# View available commands
uv run dagnostics training --help
```

## 🎮 Usage Examples

### Enhanced Remote Training (Your Current Flow + MLOps)

```bash
# Basic MLOps-enhanced training (recommended)
uv run dagnostics training remote-train \\
  --server-url http://172.16.5.60:8001 \\
  --epochs 3 \\
  --enable-mlops \\
  --experiment-name "my-experiment-v1"

# Full MLOps with hyperparameter optimization
uv run dagnostics training remote-train \\
  --server-url http://172.16.5.60:8001 \\
  --epochs 5 \\
  --enable-mlops \\
  --enable-hpo \\
  --enable-wandb \\
  --use-full-dataset
```

### Direct MLOps Training (Local)

```bash
# Run complete MLOps pipeline locally
uv run dagnostics training mlops \\
  --epochs 3 \\
  --enable-hpo \\
  --experiment-name "local-experiment"
```

### MLOps CLI Commands

```bash
# Train with full MLOps pipeline
uv run python -m mlops.cli train \\
  --train-dataset data/training/train_dataset.jsonl \\
  --epochs 3 \\
  --enable-hpo

# Validate your data quality
uv run python -m mlops.cli validate-data data/training/train_dataset.jsonl

# Run hyperparameter optimization
uv run python -m mlops.cli optimize \\
  --study-name "dagnostics-hpo" \\
  --n-trials 10

# View experiments
uv run python -m mlops.cli experiments --limit 10

# Detect data drift
uv run python -m mlops.cli detect-drift \\
  --current-dataset data/training/current.jsonl \\
  --reference-dataset data/training/reference.jsonl
```

## 📊 MLOps Features Explained

### 1. Experiment Tracking
- **MLflow**: Tracks all experiments, parameters, metrics, and artifacts
- **Weights & Biases**: Advanced experiment visualization (optional)
- **Run Comparison**: Compare multiple training runs
- **Model Registry**: Version and manage your models

### 2. Data Validation
- **Quality Assessment**: Automatic data quality scoring
- **Issue Detection**: Identifies problematic samples
- **Distribution Analysis**: Statistical data profiling
- **Drift Detection**: Monitors data changes over time

### 3. Hyperparameter Optimization
- **Optuna Integration**: State-of-the-art optimization
- **Pruning**: Early stopping of poor trials
- **Multi-objective**: Optimize multiple metrics
- **Visualization**: Optimization history plots

### 4. Pipeline Monitoring
- **Comprehensive Logging**: All stages tracked
- **Performance Metrics**: Training duration, resource usage
- **Error Handling**: Graceful failure recovery
- **Reporting**: Detailed pipeline reports

## 🎯 Your Training Workflow Options

### Option 1: Enhanced Remote Training (Recommended)
Your existing command with MLOps features:
```bash
uv run dagnostics training remote-train \\
  --server-url http://172.16.5.60:8001 \\
  --epochs 1 \\
  --enable-mlops  # Add this flag for MLOps features
```

### Option 2: Direct MLOps Training
Full local MLOps pipeline:
```bash
uv run dagnostics training mlops --epochs 3
```

### Option 3: MLOps CLI
Dedicated MLOps interface:
```bash
uv run python -m mlops.cli train --epochs 3
```

## 📈 Monitoring Your Training

### View Experiment Results
```bash
# List all experiments
uv run python -m mlops.cli experiments

# View specific experiment
uv run python -m mlops.cli experiments --experiment-name "my-experiment"

# MLflow web UI (run in background)
mlflow ui --backend-store-uri sqlite:///mlops/experiments.db
```

### Check Data Quality
```bash
# Validate your current dataset
uv run python -m mlops.cli validate-data data/training/train_dataset.jsonl --save-report

# Monitor for data drift
uv run python -m mlops.cli detect-drift \\
  --current-dataset data/training/new_data.jsonl \\
  --reference-dataset data/training/train_dataset.jsonl
```

## 🎛️ Configuration

MLOps behavior is controlled by `mlops/config.yaml`:

```yaml
# Enable/disable features
experiment_tracking:
  enable_wandb: false  # Set to true for W&B

hyperparameter_optimization:
  enable: false  # Set to true for auto-HPO

# Data validation thresholds
data_validation:
  min_samples: 50
  quality_threshold: 0.3
```

## 🔍 Troubleshooting

### MLOps Dependencies Missing
```bash
# Install dependencies
python install_mlops.py

# Or manually
pip install -r mlops/requirements.txt
```

### Experiment Tracking Issues
```bash
# Check MLOps status
uv run python -m mlops.cli status

# Reset experiment database
rm -rf mlops/experiments.db
```

### Data Quality Issues
```bash
# Check data validation
uv run python -m mlops.cli validate-data your-dataset.jsonl --save-report

# View detailed report
ls mlops/data_reports/
```

## 📁 MLOps Directory Structure

```
mlops/
├── architecture.md          # MLOps system design
├── config.yaml             # Configuration
├── requirements.txt         # Dependencies
├── cli.py                  # MLOps CLI
├── mlops_training_pipeline.py  # Main pipeline
├── experiment_tracker.py   # Experiment tracking
├── data_validator.py       # Data validation
├── hyperparameter_tuner.py # HPO system
├── experiments/            # MLflow experiments
├── artifacts/              # Training artifacts
├── models/                 # Model registry
├── data_reports/           # Validation reports
└── logs/                   # Pipeline logs
```

## 🚀 Benefits for Your Project

1. **Data Quality Assurance**: Never train on bad data again
2. **Experiment Reproducibility**: Track every training run
3. **Hyperparameter Optimization**: Find optimal settings automatically
4. **Model Performance Monitoring**: Track model degradation
5. **Professional MLOps**: Industry-standard practices
6. **Easy Integration**: Works with your current workflow

## 📞 Need Help?

- Check system status: `uv run python -m mlops.cli status`
- View help: `uv run dagnostics training --help`
- MLOps CLI help: `uv run python -m mlops.cli --help`

Your DAGnostics project is now a production-ready MLOps platform! 🎉