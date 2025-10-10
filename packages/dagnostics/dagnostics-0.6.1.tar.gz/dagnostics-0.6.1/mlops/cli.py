#!/usr/bin/env python3
"""
MLOps CLI for DAGnostics
Command-line interface for MLOps operations
"""

import click
import yaml
import logging
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Import MLOps components
from mlops.mlops_training_pipeline import run_mlops_training
from mlops.data_validator import DataValidator
from mlops.experiment_tracker import ExperimentTracker
from mlops.hyperparameter_tuner import HyperparameterTuner, HyperparameterSpace, OptimizationConfig
from mlops.model_registry import ModelRegistry

logger = logging.getLogger(__name__)


def load_config(config_path: str = "mlops/config.yaml") -> Dict[str, Any]:
    """Load MLOps configuration"""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        click.echo(f"❌ Config file not found: {config_path}")
        return {}
    except Exception as e:
        click.echo(f"❌ Error loading config: {e}")
        return {}


def setup_logging(config: Dict[str, Any]):
    """Setup logging from configuration"""
    log_config = config.get('logging', {})
    
    level = getattr(logging, log_config.get('level', 'INFO'))
    format_str = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    handlers = []
    
    # Console handler
    if log_config.get('handlers', {}).get('console', {}).get('enable', True):
        handlers.append(logging.StreamHandler())
    
    # File handler
    if log_config.get('handlers', {}).get('file', {}).get('enable', True):
        log_file = log_config.get('handlers', {}).get('file', {}).get('filename', 'mlops/training_pipeline.log')
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=handlers
    )


@click.group()
@click.option('--config', default='mlops/config.yaml', help='Path to MLOps configuration file')
@click.option('--environment', default='development', help='Environment: development, staging, production')
@click.pass_context
def mlops(ctx, config, environment):
    """MLOps CLI for DAGnostics - Production-grade ML operations"""
    
    # Load configuration
    ctx.ensure_object(dict)
    ctx.obj['config'] = load_config(config)
    ctx.obj['environment'] = environment
    
    # Apply environment-specific overrides
    if environment in ctx.obj['config'].get('environments', {}):
        env_config = ctx.obj['config']['environments'][environment]
        ctx.obj['config'] = merge_configs(ctx.obj['config'], env_config)
    
    # Setup logging
    setup_logging(ctx.obj['config'])
    
    click.echo(f"🚀 DAGnostics MLOps CLI - Environment: {environment}")


def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge configuration dictionaries"""
    result = base_config.copy()
    
    for key, value in override_config.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    
    return result


@mlops.command()
@click.option('--train-dataset', default='data/training/train_dataset.jsonl', help='Training dataset path')
@click.option('--val-dataset', default='data/training/validation_dataset.jsonl', help='Validation dataset path')
@click.option('--model-name', default='microsoft/DialoGPT-small', help='Base model name')
@click.option('--learning-rate', default=None, type=float, help='Learning rate')
@click.option('--batch-size', default=None, type=int, help='Batch size')
@click.option('--epochs', default=None, type=int, help='Number of epochs')
@click.option('--force-cpu', is_flag=True, help='Force CPU training')
@click.option('--enable-hpo', is_flag=True, help='Enable hyperparameter optimization')
@click.option('--enable-wandb', is_flag=True, help='Enable Weights & Biases tracking')
@click.option('--experiment-name', default=None, help='Experiment name')
@click.option('--model-output-name', default=None, help='Output model name')
@click.pass_context
def train(ctx, train_dataset, val_dataset, model_name, learning_rate, batch_size, 
          epochs, force_cpu, enable_hpo, enable_wandb, experiment_name, model_output_name):
    """Run MLOps training pipeline with full observability"""
    
    config = ctx.obj['config']
    
    # Use configuration defaults if not specified
    training_config = config.get('model_training', {}).get('defaults', {})
    
    params = {
        'train_dataset_path': train_dataset,
        'validation_dataset_path': val_dataset,
        'model_name': model_name or training_config.get('model_name', 'microsoft/DialoGPT-small'),
        'learning_rate': learning_rate or training_config.get('learning_rate', 5e-6),
        'batch_size': batch_size or training_config.get('batch_size', 2),
        'epochs': epochs or training_config.get('epochs', 3),
        'force_cpu': force_cpu or training_config.get('force_cpu', True),
        'enable_hyperparameter_tuning': enable_hpo or config.get('hyperparameter_optimization', {}).get('enable', False),
        'enable_wandb': enable_wandb or config.get('experiment_tracking', {}).get('enable_wandb', False),
        'experiment_name': experiment_name or f"dagnostics-{ctx.obj['environment']}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        'model_output_name': model_output_name or f"dagnostics-{ctx.obj['environment']}-model"
    }
    
    click.echo("🚀 Starting MLOps Training Pipeline")
    click.echo("="*50)
    
    for key, value in params.items():
        click.echo(f"📊 {key}: {value}")
    
    click.echo("="*50)
    
    try:
        results = run_mlops_training(**params)
        
        click.echo("🎉 Training completed successfully!")
        click.echo(f"📊 Status: {results['pipeline_status']}")
        click.echo(f"⏱️  Duration: {results['pipeline_duration_seconds']:.1f}s")
        click.echo(f"🤖 Model: {results['final_model_path']}")
        
        if results.get('experiment_run_id'):
            click.echo(f"🔬 Experiment Run: {results['experiment_run_id']}")
        
        return results
        
    except Exception as e:
        click.echo(f"❌ Training failed: {e}")
        raise click.ClickException(str(e))


@mlops.command()
@click.argument('dataset_path')
@click.option('--dataset-type', default='training', help='Dataset type: training, validation, test')
@click.option('--save-report', is_flag=True, help='Save validation report')
@click.pass_context
def validate_data(ctx, dataset_path, dataset_type, save_report):
    """Validate dataset quality and generate report"""
    
    config = ctx.obj['config']
    validation_config = config.get('data_validation', {})
    
    click.echo(f"🔍 Validating {dataset_type} dataset: {dataset_path}")
    
    try:
        validator = DataValidator(
            min_samples=validation_config.get('min_samples', 50),
            max_input_length=validation_config.get('max_input_length', 2048),
            max_output_length=validation_config.get('max_output_length', 512)
        )
        
        report = validator.validate_dataset(dataset_path, dataset_type)
        
        # Display results
        click.echo("📊 Validation Results:")
        click.echo(f"   Total samples: {report.total_samples}")
        click.echo(f"   Quality score: {report.quality_score:.2f}")
        click.echo(f"   Issues: {len(report.issues)}")
        click.echo(f"   Warnings: {len(report.warnings)}")
        
        # Show issues
        if report.issues:
            click.echo("❌ Issues found:")
            for issue in report.issues[:5]:  # Show first 5
                click.echo(f"   • {issue}")
        
        # Show warnings
        if report.warnings:
            click.echo("⚠️  Warnings:")
            for warning in report.warnings[:3]:  # Show first 3
                click.echo(f"   • {warning}")
        
        if save_report:
            report_file = f"mlops/data_reports/{dataset_type}_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            Path(report_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(report_file, 'w') as f:
                json.dump(report.to_dict(), f, indent=2, default=str)
            
            click.echo(f"💾 Report saved: {report_file}")
        
        # Exit with error if quality is too low
        min_quality = validation_config.get('quality_threshold', 0.3)
        if report.quality_score < min_quality:
            raise click.ClickException(
                f"Data quality too low: {report.quality_score:.2f} < {min_quality}"
            )
        
        click.echo("✅ Data validation passed!")
        
    except FileNotFoundError:
        raise click.ClickException(f"Dataset not found: {dataset_path}")
    except Exception as e:
        raise click.ClickException(f"Validation failed: {e}")


@mlops.command()
@click.option('--study-name', required=True, help='Optuna study name')
@click.option('--n-trials', default=10, help='Number of optimization trials')
@click.option('--timeout', default=3600, help='Optimization timeout in seconds')
@click.option('--train-dataset', default='data/training/train_dataset.jsonl', help='Training dataset path')
@click.option('--val-dataset', default='data/training/validation_dataset.jsonl', help='Validation dataset path')
@click.option('--model-name', default='microsoft/DialoGPT-small', help='Base model name')
@click.option('--force-cpu', is_flag=True, help='Force CPU training')
@click.pass_context
def optimize(ctx, study_name, n_trials, timeout, train_dataset, val_dataset, model_name, force_cpu):
    """Run hyperparameter optimization"""
    
    config = ctx.obj['config']
    hpo_config = config.get('hyperparameter_optimization', {})
    
    click.echo(f"🎯 Starting hyperparameter optimization: {study_name}")
    click.echo(f"📊 Trials: {n_trials}, Timeout: {timeout}s")
    
    try:
        # Create optimization configuration
        optimization_config = OptimizationConfig(
            study_name=study_name,
            n_trials=n_trials,
            timeout=timeout,
            max_epochs_per_trial=3 if force_cpu else 5
        )
        
        # Create hyperparameter space from config
        search_space = hpo_config.get('search_space', {})
        hyperparameter_space = HyperparameterSpace(
            learning_rate_min=search_space.get('learning_rate', {}).get('min', 1e-6),
            learning_rate_max=search_space.get('learning_rate', {}).get('max', 1e-3),
            batch_sizes=search_space.get('batch_size', {}).get('choices', [1, 2, 4]),
            epochs_min=search_space.get('epochs', {}).get('min', 1),
            epochs_max=search_space.get('epochs', {}).get('max', 5)
        )
        
        # Define training function
        def training_function(params: Dict[str, Any]) -> float:
            # Import here to avoid circular dependencies
            from dagnostics.training.fine_tuner import SLMFineTuner
            
            fine_tuner = SLMFineTuner(
                model_name=model_name,
                force_cpu=force_cpu
            )
            
            try:
                model_path = fine_tuner.train_model(
                    train_dataset_path=train_dataset,
                    validation_dataset_path=val_dataset,
                    num_epochs=params['epochs'],
                    learning_rate=params['learning_rate'],
                    batch_size=params['batch_size'],
                    model_output_name=f"hpo-{params['trial_number']}"
                )
                
                # Evaluate
                if Path(val_dataset).exists():
                    eval_results = fine_tuner.evaluate_model(model_path, val_dataset)
                    return eval_results['perplexity']
                else:
                    return 5.0  # Default reasonable value
                    
            except Exception as e:
                logger.error(f"Trial failed: {e}")
                return float('inf')
        
        # Run optimization
        tuner = HyperparameterTuner(
            config=optimization_config,
            hyperparameter_space=hyperparameter_space,
            training_function=training_function
        )
        
        results = tuner.optimize()
        
        # Display results
        click.echo("🏆 Optimization completed!")
        click.echo(f"📊 Best value: {results['best_value']:.4f}")
        click.echo("🎛️  Best parameters:")
        
        for key, value in results['best_params'].items():
            click.echo(f"   {key}: {value}")
        
        # Save results
        results_file = f"mlops/optimization_results/{study_name}_results.json"
        Path(results_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        click.echo(f"💾 Results saved: {results_file}")
        
        # Generate plots
        tuner.plot_optimization_history()
        click.echo("📊 Optimization plots generated")
        
    except Exception as e:
        raise click.ClickException(f"Optimization failed: {e}")


@mlops.command()
@click.option('--experiment-name', help='Experiment name to query')
@click.option('--run-id', help='Specific run ID to query')
@click.option('--metric', default='val_loss', help='Metric to compare')
@click.option('--limit', default=10, help='Number of runs to show')
@click.pass_context
def experiments(ctx, experiment_name, run_id, metric, limit):
    """List and compare experiments"""
    
    config = ctx.obj['config']
    tracking_config = config.get('experiment_tracking', {})
    
    try:
        tracker = ExperimentTracker(
            mlflow_tracking_uri=tracking_config.get('mlflow', {}).get('tracking_uri', 'sqlite:///mlops/experiments.db')
        )
        
        if run_id:
            # Show specific run details
            run = tracker.client.get_run(run_id)
            
            click.echo(f"🔬 Run Details: {run_id}")
            click.echo(f"📊 Status: {run.info.status}")
            click.echo(f"⏱️  Duration: {run.info.end_time - run.info.start_time if run.info.end_time else 'Running'}")
            
            if run.data.metrics:
                click.echo("📈 Metrics:")
                for key, value in run.data.metrics.items():
                    click.echo(f"   {key}: {value}")
            
            if run.data.params:
                click.echo("🎛️  Parameters:")
                for key, value in run.data.params.items():
                    click.echo(f"   {key}: {value}")
        
        elif experiment_name:
            # Compare runs in experiment
            comparison_results = tracker.compare_experiments([experiment_name], metric)
            
            click.echo(f"🏆 Best run in {experiment_name}:")
            click.echo(f"   Run ID: {comparison_results['best_run']['run_id']}")
            click.echo(f"   {metric}: {comparison_results['best_run']['metric_value']}")
            
            click.echo(f"\n📊 All runs (top {limit}):")
            for run_data in comparison_results['comparison'][:limit]:
                click.echo(f"   {run_data['run_name']}: {run_data[metric]:.4f} ({run_data['status']})")
        
        else:
            # List all experiments
            experiments_list = tracker.client.search_experiments()
            
            click.echo("📚 Available Experiments:")
            for exp in experiments_list:
                click.echo(f"   {exp.name} (ID: {exp.experiment_id})")
        
    except Exception as e:
        raise click.ClickException(f"Failed to query experiments: {e}")


@mlops.command()
@click.option('--current-dataset', required=True, help='Current dataset path')
@click.option('--reference-dataset', required=True, help='Reference dataset path')
@click.option('--threshold', default=0.05, help='Drift detection threshold')
@click.option('--save-report', is_flag=True, help='Save drift report')
@click.pass_context
def detect_drift(ctx, current_dataset, reference_dataset, threshold, save_report):
    """Detect data drift between datasets"""
    
    click.echo(f"🔍 Detecting data drift...")
    click.echo(f"   Current: {current_dataset}")
    click.echo(f"   Reference: {reference_dataset}")
    
    try:
        validator = DataValidator()
        
        drift_report = validator.detect_data_drift(
            current_dataset_path=current_dataset,
            reference_dataset_path=reference_dataset,
            threshold=threshold
        )
        
        # Display results
        click.echo("📊 Drift Detection Results:")
        click.echo(f"   Drift detected: {'Yes' if drift_report['drift_detected'] else 'No'}")
        click.echo(f"   Drift score: {drift_report['drift_score']:.4f}")
        
        # Statistical tests
        if drift_report['statistical_tests']:
            click.echo("📈 Statistical Tests:")
            for test_name, test_result in drift_report['statistical_tests'].items():
                status = "DRIFT" if test_result['drift_detected'] else "OK"
                click.echo(f"   {test_name}: {status} (p-value: {test_result['p_value']:.4f})")
        
        # Vocabulary drift
        vocab_drift = drift_report.get('distribution_shifts', {}).get('vocabulary', {})
        if vocab_drift:
            click.echo(f"📝 Vocabulary Similarity: {vocab_drift.get('jaccard_similarity', 0):.4f}")
        
        # Recommendations
        if drift_report.get('recommendations'):
            click.echo("💡 Recommendations:")
            for rec in drift_report['recommendations']:
                click.echo(f"   • {rec}")
        
        if save_report:
            report_file = f"mlops/drift_reports/drift_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            Path(report_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(report_file, 'w') as f:
                json.dump(drift_report, f, indent=2, default=str)
            
            click.echo(f"💾 Report saved: {report_file}")
        
        # Exit with error if significant drift detected
        if drift_report['drift_detected']:
            click.echo("⚠️  Significant drift detected - consider retraining!")
            
    except Exception as e:
        raise click.ClickException(f"Drift detection failed: {e}")


@mlops.command()
@click.argument('model_name')
@click.option('--version', default='latest', help='Model version')
@click.pass_context
def get_model(ctx, model_name, version):
    """Get model information from registry"""
    
    try:
        registry = ModelRegistry()
        model = registry.get_model(model_name, version)
        
        if not model:
            click.echo(f"❌ Model not found: {model_name} v{version}")
            return
        
        click.echo(f"🤖 Model: {model.name} v{model.version}")
        click.echo(f"📊 Status: {model.stage}")
        click.echo(f"📦 Size: {model.model_size_mb:.1f} MB")
        click.echo(f"🏷️  Model ID: {model.model_id}")
        click.echo(f"📅 Created: {model.created_at}")
        click.echo(f"👤 Created by: {model.created_by}")
        click.echo(f"📁 Path: {model.model_path}")
        
        if model.metrics:
            click.echo("📈 Metrics:")
            for metric, value in model.metrics.items():
                click.echo(f"   {metric}: {value}")
        
        if model.tags:
            click.echo("🏷️  Tags:")
            for tag, value in model.tags.items():
                click.echo(f"   {tag}: {value}")
                
    except Exception as e:
        click.echo(f"❌ Failed to get model: {e}")


@mlops.command()
@click.option('--stage', help='Filter by stage (staging, production, archived)')
@click.option('--model-type', help='Filter by model type')
@click.option('--limit', default=10, help='Maximum number of models to show')
@click.pass_context
def list_models(ctx, stage, model_type, limit):
    """List models in registry"""
    
    try:
        registry = ModelRegistry()
        models = registry.list_models(stage=stage, model_type=model_type)
        
        if not models:
            click.echo("📝 No models found in registry")
            return
        
        click.echo("🏛️  Model Registry:")
        click.echo("=" * 80)
        
        for i, model in enumerate(models[:limit]):
            click.echo(f"{i+1}. {model.name} v{model.version}")
            click.echo(f"   Stage: {model.stage}")
            click.echo(f"   Size: {model.model_size_mb:.1f} MB")
            click.echo(f"   Created: {model.created_at}")
            
            if model.metrics:
                key_metrics = dict(list(model.metrics.items())[:3])  # Show first 3 metrics
                metrics_str = ", ".join([f"{k}: {v}" for k, v in key_metrics.items()])
                click.echo(f"   Metrics: {metrics_str}")
            
            click.echo("")
        
        if len(models) > limit:
            click.echo(f"... and {len(models) - limit} more models")
            
    except Exception as e:
        click.echo(f"❌ Failed to list models: {e}")


@mlops.command()
@click.argument('model_name')
@click.argument('version')
@click.argument('target_stage')
@click.pass_context
def promote_model(ctx, model_name, version, target_stage):
    """Promote model to different stage"""
    
    if target_stage not in ['staging', 'production', 'archived']:
        click.echo("❌ Invalid stage. Use: staging, production, or archived")
        return
    
    try:
        registry = ModelRegistry()
        success = registry.promote_model(model_name, version, target_stage)
        
        if success:
            click.echo(f"🚀 Model promoted: {model_name} v{version} -> {target_stage}")
        else:
            click.echo(f"❌ Failed to promote model: {model_name} v{version}")
            
    except Exception as e:
        click.echo(f"❌ Promotion failed: {e}")


@mlops.command()
@click.argument('model_a_name')
@click.argument('model_b_name')
@click.option('--version-a', default='latest', help='Version of first model')
@click.option('--version-b', default='latest', help='Version of second model')
@click.pass_context
def compare_models(ctx, model_a_name, model_b_name, version_a, version_b):
    """Compare two models"""
    
    try:
        registry = ModelRegistry()
        comparison = registry.compare_models(model_a_name, model_b_name, version_a, version_b)
        
        if not comparison:
            click.echo("❌ Could not compare models")
            return
        
        click.echo(f"📊 Model Comparison: {comparison.model_a} vs {comparison.model_b}")
        click.echo("=" * 60)
        click.echo(f"🏆 Better Model: {comparison.better_model}")
        click.echo(f"📈 Summary: {comparison.improvement_summary}")
        click.echo("")
        
        click.echo("📋 Detailed Metrics:")
        for metric, values in comparison.comparison_metrics.items():
            click.echo(f"  {metric}:")
            for key, value in values.items():
                if isinstance(value, float):
                    click.echo(f"    {key}: {value:.4f}")
                else:
                    click.echo(f"    {key}: {value}")
            click.echo("")
            
    except Exception as e:
        click.echo(f"❌ Comparison failed: {e}")


@mlops.command()
@click.argument('model_name')
@click.option('--version', default='latest', help='Model version')
@click.pass_context
def model_lineage(ctx, model_name, version):
    """Show model training lineage and provenance"""
    
    try:
        registry = ModelRegistry()
        lineage = registry.get_model_lineage(model_name, version)
        
        if not lineage:
            click.echo(f"❌ No lineage found for: {model_name} v{version}")
            return
        
        click.echo(f"🔗 Model Lineage: {model_name} v{version}")
        click.echo("=" * 50)
        
        # Training lineage
        training = lineage.get('training_lineage', {})
        if training:
            click.echo("🚀 Training Information:")
            click.echo(f"  Base Model: {training.get('base_model', 'N/A')}")
            click.echo(f"  Training Dataset: {training.get('training_dataset', 'N/A')}")
            click.echo(f"  Duration: {training.get('training_duration', 0):.1f}s")
            click.echo("")
        
        # Experiment tracking
        experiment = lineage.get('experiment_tracking', {})
        if experiment and experiment.get('experiment_id'):
            click.echo("🔬 Experiment Tracking:")
            click.echo(f"  Experiment ID: {experiment.get('experiment_id')}")
            click.echo(f"  Run ID: {experiment.get('run_id')}")
            if experiment.get('mlflow_uri'):
                click.echo(f"  MLflow URL: {experiment.get('mlflow_uri')}")
            click.echo("")
        
        # Model artifacts
        artifacts = lineage.get('model_artifacts', {})
        if artifacts:
            click.echo("📦 Model Artifacts:")
            click.echo(f"  Path: {artifacts.get('model_path', 'N/A')}")
            click.echo(f"  Size: {artifacts.get('model_size_mb', 0):.1f} MB")
            click.echo(f"  Hash: {artifacts.get('model_hash', 'N/A')}")
            
    except Exception as e:
        click.echo(f"❌ Failed to get lineage: {e}")


@mlops.command()
@click.pass_context
def status(ctx):
    """Show MLOps system status"""
    
    config = ctx.obj['config']
    
    click.echo("📊 DAGnostics MLOps System Status")
    click.echo("="*40)
    
    # Environment
    click.echo(f"🌍 Environment: {ctx.obj['environment']}")
    
    # Configuration
    click.echo(f"⚙️  Configuration loaded: {'✅' if config else '❌'}")
    
    # Check MLflow
    try:
        import mlflow
        mlflow.set_tracking_uri(config.get('experiment_tracking', {}).get('mlflow', {}).get('tracking_uri', 'sqlite:///mlops/experiments.db'))
        experiments = mlflow.search_experiments()
        click.echo(f"🔬 MLflow: ✅ ({len(experiments)} experiments)")
    except Exception as e:
        click.echo(f"🔬 MLflow: ❌ ({e})")
    
    # Check data directories
    data_paths = ['data/training', 'mlops/artifacts', 'mlops/models']
    for path in data_paths:
        exists = Path(path).exists()
        click.echo(f"📁 {path}: {'✅' if exists else '❌'}")
    
    # Check datasets
    train_dataset = config.get('model_training', {}).get('defaults', {}).get('train_dataset_path', 'data/training/train_dataset.jsonl')
    val_dataset = config.get('model_training', {}).get('defaults', {}).get('validation_dataset_path', 'data/training/validation_dataset.jsonl')
    
    click.echo(f"📊 Training dataset: {'✅' if Path(train_dataset).exists() else '❌'} ({train_dataset})")
    click.echo(f"📊 Validation dataset: {'✅' if Path(val_dataset).exists() else '❌'} ({val_dataset})")
    
    # Check model registry
    try:
        registry = ModelRegistry()
        models = registry.list_models()
        click.echo(f"🏛️  Model registry: ✅ ({len(models)} models registered)")
        
        # Show production models
        production_models = [m for m in models if m.stage == 'production']
        if production_models:
            click.echo(f"🚀 Production models: {len(production_models)}")
        
    except Exception as e:
        click.echo(f"🏛️  Model registry: ❌ ({e})")
    
    # System resources
    try:
        import psutil
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.')
        
        click.echo("💻 System Resources:")
        click.echo(f"   CPU: {cpu_percent}%")
        click.echo(f"   Memory: {memory.percent}% ({memory.used // (1024**3):.1f}GB / {memory.total // (1024**3):.1f}GB)")
        click.echo(f"   Disk: {disk.percent}% ({disk.free // (1024**3):.1f}GB free)")
        
    except ImportError:
        click.echo("💻 System Resources: ❌ (psutil not available)")
    except Exception as e:
        click.echo(f"💻 System Resources: ❌ ({e})")


if __name__ == '__main__':
    mlops()