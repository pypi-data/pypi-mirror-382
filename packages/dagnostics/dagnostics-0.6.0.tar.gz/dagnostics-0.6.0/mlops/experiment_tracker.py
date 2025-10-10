#!/usr/bin/env python3
"""
MLOps Experiment Tracking System for DAGnostics
Integrates MLflow with comprehensive experiment management
"""

import mlflow
import mlflow.pytorch
from mlflow.tracking import MlflowClient
import torch
import wandb
from pathlib import Path
import json
import hashlib
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging
from dataclasses import dataclass, asdict
import numpy as np
from contextlib import contextmanager

logger = logging.getLogger(__name__)


@dataclass
class ExperimentConfig:
    """Configuration for ML experiments"""
    
    # Model parameters
    model_name: str
    learning_rate: float
    batch_size: int
    epochs: int
    max_length: int
    
    # Data parameters
    train_dataset_path: str
    validation_dataset_path: Optional[str]
    dataset_size: int
    
    # Training parameters
    optimizer: str
    scheduler: Optional[str]
    use_quantization: bool
    force_cpu: bool
    
    # Experiment metadata
    experiment_name: str
    run_name: Optional[str] = None
    tags: Dict[str, Any] = None
    description: Optional[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}
        if self.run_name is None:
            self.run_name = f"{self.model_name.split('/')[-1]}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


class ExperimentTracker:
    """
    Comprehensive experiment tracking for DAGnostics training
    Supports MLflow and Weights & Biases integration
    """
    
    def __init__(
        self,
        mlflow_tracking_uri: str = "sqlite:///mlops/experiments.db",
        wandb_project: Optional[str] = "dagnostics-training",
        enable_wandb: bool = False
    ):
        self.mlflow_tracking_uri = mlflow_tracking_uri
        self.wandb_project = wandb_project
        self.enable_wandb = enable_wandb
        
        # Initialize MLflow
        mlflow.set_tracking_uri(mlflow_tracking_uri)
        self.client = MlflowClient()
        
        # Create MLflow directories
        Path("mlops").mkdir(exist_ok=True)
        
        # Current experiment state
        self.current_experiment = None
        self.current_run = None
        self.config = None
        
        logger.info(f"🔬 Experiment tracker initialized")
        logger.info(f"📊 MLflow URI: {mlflow_tracking_uri}")
        if enable_wandb:
            logger.info(f"🏃 W&B Project: {wandb_project}")
    
    @contextmanager
    def start_experiment(self, config: ExperimentConfig):
        """
        Context manager for experiment tracking
        Automatically handles experiment lifecycle
        """
        try:
            # Create or get experiment
            experiment = self._get_or_create_experiment(config.experiment_name)
            self.current_experiment = experiment
            self.config = config
            
            # Generate experiment hash for reproducibility
            config_hash = self._generate_config_hash(config)
            
            # Start MLflow run
            with mlflow.start_run(
                experiment_id=experiment.experiment_id,
                run_name=config.run_name,
                tags={
                    **config.tags,
                    "config_hash": config_hash,
                    "framework": "transformers",
                    "task": "error_extraction"
                },
                description=config.description
            ) as run:
                self.current_run = run
                
                # Log configuration
                self._log_config(config)
                
                # Initialize W&B if enabled
                if self.enable_wandb:
                    wandb.init(
                        project=self.wandb_project,
                        name=config.run_name,
                        config=asdict(config),
                        tags=list(config.tags.keys()),
                        notes=config.description
                    )
                
                logger.info(f"🚀 Started experiment: {config.experiment_name}")
                logger.info(f"🏃 Run: {config.run_name} ({run.info.run_id})")
                
                yield self
                
        except Exception as e:
            logger.error(f"❌ Experiment failed: {e}")
            self.log_error(str(e))
            raise
        
        finally:
            # Cleanup
            if self.enable_wandb:
                wandb.finish()
            
            self.current_run = None
            self.current_experiment = None
            self.config = None
            
            logger.info("✅ Experiment completed")
    
    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        """Log training/validation metrics"""
        try:
            # Log to MLflow
            for key, value in metrics.items():
                mlflow.log_metric(key, value, step=step)
            
            # Log to W&B
            if self.enable_wandb:
                wandb.log(metrics, step=step)
            
            logger.debug(f"📊 Logged metrics: {metrics}")
            
        except Exception as e:
            logger.error(f"❌ Failed to log metrics: {e}")
    
    def log_params(self, params: Dict[str, Any]):
        """Log hyperparameters"""
        try:
            mlflow.log_params(params)
            logger.debug(f"🎛️  Logged params: {params}")
            
        except Exception as e:
            logger.error(f"❌ Failed to log params: {e}")
    
    def log_artifacts(self, artifacts: Dict[str, str]):
        """Log files and artifacts"""
        try:
            for name, path in artifacts.items():
                if Path(path).exists():
                    mlflow.log_artifact(path, name)
                    logger.debug(f"📁 Logged artifact: {name} -> {path}")
                else:
                    logger.warning(f"⚠️  Artifact not found: {path}")
                    
        except Exception as e:
            logger.error(f"❌ Failed to log artifacts: {e}")
    
    def log_model(
        self,
        model,
        model_path: str,
        input_example: Optional[Any] = None,
        signature: Optional[Any] = None
    ):
        """Log trained model"""
        try:
            # Log model to MLflow
            mlflow.pytorch.log_model(
                pytorch_model=model,
                artifact_path="model",
                conda_env=self._get_conda_env(),
                input_example=input_example,
                signature=signature
            )
            
            # Log model files
            if Path(model_path).exists():
                mlflow.log_artifacts(model_path, "model_files")
            
            logger.info(f"🤖 Model logged: {model_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to log model: {e}")
    
    def log_dataset_info(self, dataset_info: Dict[str, Any]):
        """Log dataset information and statistics"""
        try:
            # Log basic dataset info
            self.log_params({
                f"dataset_{k}": v for k, v in dataset_info.items()
                if isinstance(v, (str, int, float, bool))
            })
            
            # Log dataset statistics as metrics
            if "statistics" in dataset_info:
                stats = dataset_info["statistics"]
                for key, value in stats.items():
                    if isinstance(value, (int, float)):
                        mlflow.log_metric(f"dataset_{key}", value)
            
            # Save detailed info as JSON
            dataset_json_path = "dataset_info.json"
            with open(dataset_json_path, "w") as f:
                json.dump(dataset_info, f, indent=2, default=str)
            
            mlflow.log_artifact(dataset_json_path, "data")
            Path(dataset_json_path).unlink()  # Clean up
            
            logger.info("📊 Dataset info logged")
            
        except Exception as e:
            logger.error(f"❌ Failed to log dataset info: {e}")
    
    def log_training_progress(
        self,
        epoch: int,
        step: int,
        loss: float,
        learning_rate: float,
        additional_metrics: Optional[Dict[str, float]] = None
    ):
        """Log training progress with structured metrics"""
        try:
            metrics = {
                "epoch": epoch,
                "step": step,
                "train_loss": loss,
                "learning_rate": learning_rate
            }
            
            if additional_metrics:
                metrics.update(additional_metrics)
            
            self.log_metrics(metrics, step=step)
            
            # Log to W&B with custom plots
            if self.enable_wandb:
                wandb.log({
                    "training/loss_curve": wandb.plot.line(
                        table=wandb.Table(
                            data=[[step, loss]],
                            columns=["step", "loss"]
                        ),
                        x="step",
                        y="loss",
                        title="Training Loss"
                    )
                }, step=step)
            
        except Exception as e:
            logger.error(f"❌ Failed to log training progress: {e}")
    
    def log_validation_results(
        self,
        epoch: int,
        val_loss: float,
        metrics: Dict[str, float]
    ):
        """Log validation results"""
        try:
            validation_metrics = {
                "val_loss": val_loss,
                "epoch": epoch,
                **{f"val_{k}": v for k, v in metrics.items()}
            }
            
            self.log_metrics(validation_metrics)
            
            logger.info(f"📈 Validation logged - Loss: {val_loss:.4f}")
            
        except Exception as e:
            logger.error(f"❌ Failed to log validation results: {e}")
    
    def log_error(self, error_message: str):
        """Log training errors"""
        try:
            mlflow.set_tag("status", "failed")
            mlflow.set_tag("error", error_message)
            
            if self.enable_wandb:
                wandb.alert(
                    title="Training Failed",
                    text=error_message,
                    level=wandb.AlertLevel.ERROR
                )
            
            logger.error(f"💥 Error logged: {error_message}")
            
        except Exception as e:
            logger.error(f"❌ Failed to log error: {e}")
    
    def compare_experiments(
        self,
        experiment_names: List[str],
        metric: str = "val_loss"
    ) -> Dict[str, Any]:
        """Compare experiments and return best performing run"""
        try:
            best_run = None
            best_metric = float('inf')
            comparison_data = []
            
            for exp_name in experiment_names:
                experiment = self._get_or_create_experiment(exp_name)
                runs = self.client.search_runs(
                    experiment_ids=[experiment.experiment_id],
                    order_by=[f"metrics.{metric} ASC"],
                    max_results=10
                )
                
                for run in runs:
                    if metric in run.data.metrics:
                        metric_value = run.data.metrics[metric]
                        comparison_data.append({
                            "experiment": exp_name,
                            "run_id": run.info.run_id,
                            "run_name": run.data.tags.get("mlflow.runName", "Unknown"),
                            metric: metric_value,
                            "status": run.info.status
                        })
                        
                        if metric_value < best_metric:
                            best_metric = metric_value
                            best_run = run
            
            result = {
                "best_run": {
                    "run_id": best_run.info.run_id if best_run else None,
                    "experiment": best_run.info.experiment_id if best_run else None,
                    "metric_value": best_metric if best_run else None
                },
                "comparison": comparison_data
            }
            
            logger.info(f"🏆 Best run: {result['best_run']}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to compare experiments: {e}")
            return {}
    
    def _get_or_create_experiment(self, name: str):
        """Get existing experiment or create new one"""
        try:
            experiment = mlflow.get_experiment_by_name(name)
            if experiment is None:
                experiment_id = mlflow.create_experiment(name)
                experiment = mlflow.get_experiment(experiment_id)
            return experiment
        except Exception as e:
            logger.error(f"❌ Failed to get/create experiment: {e}")
            raise
    
    def _log_config(self, config: ExperimentConfig):
        """Log experiment configuration"""
        config_dict = asdict(config)
        
        # Separate params and tags
        params = {k: v for k, v in config_dict.items() 
                 if k not in ['tags', 'description'] and v is not None}
        
        self.log_params(params)
        
        # Set additional tags
        mlflow.set_tag("model_family", config.model_name.split('/')[0])
        mlflow.set_tag("training_mode", "cpu" if config.force_cpu else "gpu")
        mlflow.set_tag("quantization", str(config.use_quantization))
    
    def _generate_config_hash(self, config: ExperimentConfig) -> str:
        """Generate hash for experiment reproducibility"""
        config_str = json.dumps(asdict(config), sort_keys=True, default=str)
        return hashlib.md5(config_str.encode()).hexdigest()[:8]
    
    def _get_conda_env(self) -> Dict[str, Any]:
        """Get conda environment for model deployment"""
        return {
            "channels": ["defaults", "conda-forge"],
            "dependencies": [
                "python=3.10",
                "pytorch",
                "transformers",
                "tokenizers",
                {
                    "pip": [
                        "mlflow",
                        "dagnostics"
                    ]
                }
            ],
            "name": "dagnostics-env"
        }


# Convenience functions for integration
def setup_mlops_logging():
    """Setup MLOps logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('mlops/training.log')
        ]
    )


def create_experiment_config_from_args(**kwargs) -> ExperimentConfig:
    """Create experiment config from training arguments"""
    
    # Set defaults for missing values
    defaults = {
        'model_name': 'microsoft/DialoGPT-small',
        'learning_rate': 2e-4,
        'batch_size': 4,
        'epochs': 3,
        'max_length': 512,
        'train_dataset_path': 'data/training/train_dataset.jsonl',
        'validation_dataset_path': 'data/training/validation_dataset.jsonl',
        'dataset_size': 0,
        'optimizer': 'adamw_torch',
        'scheduler': None,
        'use_quantization': False,
        'force_cpu': True,
        'experiment_name': 'dagnostics-error-extraction',
        'tags': {}
    }
    
    # Merge with provided arguments
    config_dict = {**defaults, **kwargs}
    
    return ExperimentConfig(**config_dict)


if __name__ == "__main__":
    # Example usage
    setup_mlops_logging()
    
    config = ExperimentConfig(
        model_name="microsoft/DialoGPT-small",
        learning_rate=5e-6,
        batch_size=2,
        epochs=3,
        max_length=512,
        train_dataset_path="data/training/train_dataset.jsonl",
        validation_dataset_path="data/training/validation_dataset.jsonl",
        dataset_size=12,
        optimizer="adamw_torch",
        use_quantization=False,
        force_cpu=True,
        experiment_name="test-experiment",
        description="Testing MLOps integration"
    )
    
    tracker = ExperimentTracker(enable_wandb=False)
    
    with tracker.start_experiment(config) as exp:
        # Simulate training
        for epoch in range(3):
            for step in range(10):
                loss = 10.0 - (epoch * 2 + step * 0.1)  # Fake decreasing loss
                exp.log_training_progress(
                    epoch=epoch,
                    step=epoch * 10 + step,
                    loss=loss,
                    learning_rate=5e-6
                )
            
            # Validation
            val_loss = 8.0 - epoch * 1.5
            exp.log_validation_results(
                epoch=epoch,
                val_loss=val_loss,
                metrics={"accuracy": 0.7 + epoch * 0.1}
            )
        
        print("✅ MLOps experiment tracking demo completed!")