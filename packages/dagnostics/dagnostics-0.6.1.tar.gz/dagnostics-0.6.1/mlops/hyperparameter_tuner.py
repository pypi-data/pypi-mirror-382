#!/usr/bin/env python3
"""
MLOps Hyperparameter Optimization System for DAGnostics
Automated hyperparameter tuning with Optuna integration
"""

import optuna
from optuna.integration.mlflow import MLflowCallback
import mlflow
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
import numpy as np
from datetime import datetime
import joblib
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class HyperparameterSpace:
    """Definition of hyperparameter search space"""
    
    # Learning rate range
    learning_rate_min: float = 1e-6
    learning_rate_max: float = 1e-3
    learning_rate_log: bool = True
    
    # Batch size options
    batch_sizes: List[int] = None
    
    # Epoch range
    epochs_min: int = 1
    epochs_max: int = 10
    
    # Model architecture
    max_length_options: List[int] = None
    
    # Optimizer options
    optimizer_choices: List[str] = None
    
    # Regularization
    weight_decay_min: float = 1e-6
    weight_decay_max: float = 1e-2
    weight_decay_log: bool = True
    
    # LoRA parameters
    lora_r_options: List[int] = None
    lora_alpha_options: List[int] = None
    lora_dropout_min: float = 0.0
    lora_dropout_max: float = 0.3
    
    def __post_init__(self):
        if self.batch_sizes is None:
            self.batch_sizes = [1, 2, 4, 8]
        if self.max_length_options is None:
            self.max_length_options = [256, 512, 1024]
        if self.optimizer_choices is None:
            self.optimizer_choices = ["adamw_torch", "adamw_torch_fused", "adafactor"]
        if self.lora_r_options is None:
            self.lora_r_options = [4, 8, 16, 32]
        if self.lora_alpha_options is None:
            self.lora_alpha_options = [8, 16, 32, 64]


@dataclass
class OptimizationConfig:
    """Configuration for hyperparameter optimization"""
    
    study_name: str
    n_trials: int = 20
    timeout: Optional[int] = None  # seconds
    
    # Optimization objective
    metric_name: str = "val_loss"
    direction: str = "minimize"  # "minimize" or "maximize"
    
    # Pruning configuration
    enable_pruning: bool = True
    pruner_type: str = "median"  # "median", "hyperband", "successive_halving"
    
    # Parallel optimization
    n_jobs: int = 1
    
    # Early stopping
    early_stopping_patience: int = 5
    early_stopping_threshold: float = 0.01
    
    # Resource constraints
    max_epochs_per_trial: int = 5
    max_time_per_trial: int = 3600  # 1 hour
    
    # MLflow integration
    mlflow_tracking_uri: str = "sqlite:///mlops/optimization.db"
    mlflow_experiment_name: str = "hyperparameter-optimization"


class HyperparameterTuner:
    """
    Advanced hyperparameter optimization with Optuna
    Integrates with MLflow for experiment tracking
    """
    
    def __init__(
        self,
        config: OptimizationConfig,
        hyperparameter_space: HyperparameterSpace,
        training_function: Callable[[Dict[str, Any]], float]
    ):
        self.config = config
        self.hyperparameter_space = hyperparameter_space
        self.training_function = training_function
        
        # Initialize MLflow
        mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        
        # Create storage for study
        self.storage_path = f"mlops/optuna_studies/{config.study_name}.db"
        Path(self.storage_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.storage = f"sqlite:///{self.storage_path}"
        
        # Initialize study
        self.study = None
        self._setup_study()
        
        logger.info(f"🎯 Hyperparameter tuner initialized: {config.study_name}")
    
    def optimize(self) -> Dict[str, Any]:
        """
        Run hyperparameter optimization
        Returns best parameters and optimization results
        """
        logger.info(f"🚀 Starting hyperparameter optimization: {self.config.n_trials} trials")
        
        # Setup MLflow callback
        mlflow_callback = MLflowCallback(
            tracking_uri=self.config.mlflow_tracking_uri,
            create_experiment=True
        )
        
        try:
            # Run optimization
            self.study.optimize(
                self._objective,
                n_trials=self.config.n_trials,
                timeout=self.config.timeout,
                n_jobs=self.config.n_jobs,
                callbacks=[mlflow_callback],
                show_progress_bar=True
            )
            
            # Get results
            best_params = self.study.best_params
            best_value = self.study.best_value
            best_trial = self.study.best_trial
            
            # Generate optimization report
            optimization_report = self._generate_optimization_report()
            
            # Save results
            self._save_optimization_results(optimization_report)
            
            logger.info(f"🏆 Optimization completed!")
            logger.info(f"📊 Best value: {best_value:.6f}")
            logger.info(f"🎛️  Best params: {best_params}")
            
            return {
                'best_params': best_params,
                'best_value': best_value,
                'best_trial_number': best_trial.number,
                'optimization_report': optimization_report,
                'study_name': self.config.study_name
            }
            
        except Exception as e:
            logger.error(f"❌ Optimization failed: {e}")
            raise
    
    def get_optimization_history(self) -> pd.DataFrame:
        """Get optimization history as DataFrame"""
        
        trials_df = self.study.trials_dataframe()
        
        # Add custom columns
        trials_df['trial_duration'] = trials_df['datetime_complete'] - trials_df['datetime_start']
        trials_df['is_best'] = trials_df['value'] == self.study.best_value
        
        return trials_df
    
    def plot_optimization_history(self, save_path: Optional[str] = None):
        """Generate optimization visualization plots"""
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            # Create plots directory
            plots_dir = Path("mlops/optimization_plots")
            plots_dir.mkdir(parents=True, exist_ok=True)
            
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            
            # Plot 1: Optimization history
            optuna.visualization.matplotlib.plot_optimization_history(self.study, ax=axes[0, 0])
            axes[0, 0].set_title('Optimization History')
            
            # Plot 2: Parameter importances
            try:
                optuna.visualization.matplotlib.plot_param_importances(self.study, ax=axes[0, 1])
                axes[0, 1].set_title('Parameter Importances')
            except:
                axes[0, 1].text(0.5, 0.5, 'Not enough trials\nfor importance analysis', 
                              ha='center', va='center', transform=axes[0, 1].transAxes)
                axes[0, 1].set_title('Parameter Importances (N/A)')
            
            # Plot 3: Parallel coordinate plot (for top trials)
            try:
                optuna.visualization.matplotlib.plot_parallel_coordinate(
                    self.study, ax=axes[1, 0], params=list(self.study.best_params.keys())[:4]
                )
                axes[1, 0].set_title('Parallel Coordinate Plot')
            except:
                axes[1, 0].text(0.5, 0.5, 'Unable to generate\nparallel coordinate plot', 
                              ha='center', va='center', transform=axes[1, 0].transAxes)
            
            # Plot 4: Trial timeline
            trials_df = self.get_optimization_history()
            if not trials_df.empty:
                axes[1, 1].plot(trials_df['number'], trials_df['value'], marker='o', alpha=0.7)
                axes[1, 1].axhline(y=self.study.best_value, color='r', linestyle='--', alpha=0.7)
                axes[1, 1].set_xlabel('Trial Number')
                axes[1, 1].set_ylabel('Objective Value')
                axes[1, 1].set_title('Trial Progress')
                axes[1, 1].grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Save plot
            if save_path is None:
                save_path = plots_dir / f"{self.config.study_name}_optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"📊 Optimization plots saved: {save_path}")
            
        except ImportError:
            logger.warning("⚠️  Matplotlib not available - skipping plots")
        except Exception as e:
            logger.error(f"❌ Failed to generate plots: {e}")
    
    def suggest_next_trial_params(self) -> Dict[str, Any]:
        """Suggest parameters for next trial (for manual optimization)"""
        trial = self.study.ask()
        params = self._suggest_hyperparameters(trial)
        return params
    
    def report_trial_result(self, params: Dict[str, Any], value: float):
        """Report result for manual trial"""
        # Find the trial with matching parameters
        for trial in self.study.trials:
            if trial.params == params and trial.state == optuna.trial.TrialState.RUNNING:
                self.study.tell(trial, value)
                break
    
    def _setup_study(self):
        """Initialize Optuna study"""
        
        # Setup pruner
        if self.config.enable_pruning:
            if self.config.pruner_type == "median":
                pruner = optuna.pruners.MedianPruner(
                    n_startup_trials=5,
                    n_warmup_steps=10,
                    interval_steps=1
                )
            elif self.config.pruner_type == "hyperband":
                pruner = optuna.pruners.HyperbandPruner(
                    min_resource=1,
                    max_resource=self.config.max_epochs_per_trial,
                    reduction_factor=3
                )
            else:  # successive_halving
                pruner = optuna.pruners.SuccessiveHalvingPruner()
        else:
            pruner = optuna.pruners.NopPruner()
        
        # Create study
        direction = self.config.direction
        
        self.study = optuna.create_study(
            study_name=self.config.study_name,
            storage=self.storage,
            direction=direction,
            pruner=pruner,
            load_if_exists=True
        )
        
        logger.info(f"📚 Study created/loaded: {len(self.study.trials)} existing trials")
    
    def _objective(self, trial: optuna.Trial) -> float:
        """
        Objective function for optimization
        This is called for each trial
        """
        try:
            # Suggest hyperparameters
            params = self._suggest_hyperparameters(trial)
            
            # Add trial metadata
            params['trial_number'] = trial.number
            params['study_name'] = self.config.study_name
            
            logger.info(f"🧪 Trial {trial.number}: {params}")
            
            # Run training with suggested parameters
            result = self.training_function(params)
            
            # Handle pruning
            if isinstance(result, dict) and 'intermediate_values' in result:
                # Report intermediate values for pruning
                for step, value in result['intermediate_values'].items():
                    trial.report(value, step)
                    
                    # Check if trial should be pruned
                    if trial.should_prune():
                        logger.info(f"✂️  Trial {trial.number} pruned at step {step}")
                        raise optuna.TrialPruned()
                
                final_result = result['final_value']
            else:
                final_result = float(result)
            
            logger.info(f"📊 Trial {trial.number} completed: {final_result:.6f}")
            
            return final_result
            
        except optuna.TrialPruned:
            raise
        except Exception as e:
            logger.error(f"❌ Trial {trial.number} failed: {e}")
            # Return a poor result so the trial is marked as failed but optimization continues
            return float('inf') if self.config.direction == "minimize" else float('-inf')
    
    def _suggest_hyperparameters(self, trial: optuna.Trial) -> Dict[str, Any]:
        """Suggest hyperparameters for a trial"""
        params = {}
        
        # Learning rate
        if self.hyperparameter_space.learning_rate_log:
            params['learning_rate'] = trial.suggest_float(
                'learning_rate',
                self.hyperparameter_space.learning_rate_min,
                self.hyperparameter_space.learning_rate_max,
                log=True
            )
        else:
            params['learning_rate'] = trial.suggest_float(
                'learning_rate',
                self.hyperparameter_space.learning_rate_min,
                self.hyperparameter_space.learning_rate_max
            )
        
        # Batch size
        params['batch_size'] = trial.suggest_categorical(
            'batch_size',
            self.hyperparameter_space.batch_sizes
        )
        
        # Epochs
        params['epochs'] = trial.suggest_int(
            'epochs',
            self.hyperparameter_space.epochs_min,
            min(self.hyperparameter_space.epochs_max, self.config.max_epochs_per_trial)
        )
        
        # Max length
        params['max_length'] = trial.suggest_categorical(
            'max_length',
            self.hyperparameter_space.max_length_options
        )
        
        # Optimizer
        params['optimizer'] = trial.suggest_categorical(
            'optimizer',
            self.hyperparameter_space.optimizer_choices
        )
        
        # Weight decay
        if self.hyperparameter_space.weight_decay_log:
            params['weight_decay'] = trial.suggest_float(
                'weight_decay',
                self.hyperparameter_space.weight_decay_min,
                self.hyperparameter_space.weight_decay_max,
                log=True
            )
        else:
            params['weight_decay'] = trial.suggest_float(
                'weight_decay',
                self.hyperparameter_space.weight_decay_min,
                self.hyperparameter_space.weight_decay_max
            )
        
        # LoRA parameters (if using LoRA)
        params['lora_r'] = trial.suggest_categorical(
            'lora_r',
            self.hyperparameter_space.lora_r_options
        )
        
        params['lora_alpha'] = trial.suggest_categorical(
            'lora_alpha',
            self.hyperparameter_space.lora_alpha_options
        )
        
        params['lora_dropout'] = trial.suggest_float(
            'lora_dropout',
            self.hyperparameter_space.lora_dropout_min,
            self.hyperparameter_space.lora_dropout_max
        )
        
        return params
    
    def _generate_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report"""
        
        trials_df = self.get_optimization_history()
        
        # Basic statistics
        n_completed_trials = len(trials_df[trials_df['state'] == 'COMPLETE'])
        n_pruned_trials = len(trials_df[trials_df['state'] == 'PRUNED'])
        n_failed_trials = len(trials_df[trials_df['state'] == 'FAIL'])
        
        # Performance statistics
        if n_completed_trials > 0:
            completed_values = trials_df[trials_df['state'] == 'COMPLETE']['value']
            
            performance_stats = {
                'best_value': float(self.study.best_value),
                'worst_value': float(completed_values.max() if self.config.direction == "minimize" else completed_values.min()),
                'mean_value': float(completed_values.mean()),
                'std_value': float(completed_values.std()),
                'median_value': float(completed_values.median())
            }
        else:
            performance_stats = {}
        
        # Parameter importance
        try:
            param_importance = optuna.importance.get_param_importances(self.study)
        except:
            param_importance = {}
        
        # Trial duration analysis
        if not trials_df.empty and 'trial_duration' in trials_df.columns:
            duration_stats = {
                'avg_trial_duration_seconds': float(trials_df['trial_duration'].dt.total_seconds().mean()),
                'max_trial_duration_seconds': float(trials_df['trial_duration'].dt.total_seconds().max()),
                'min_trial_duration_seconds': float(trials_df['trial_duration'].dt.total_seconds().min())
            }
        else:
            duration_stats = {}
        
        report = {
            'study_name': self.config.study_name,
            'optimization_config': asdict(self.config),
            'hyperparameter_space': asdict(self.hyperparameter_space),
            'results': {
                'best_params': self.study.best_params,
                'best_value': self.study.best_value,
                'best_trial_number': self.study.best_trial.number,
                'n_trials': len(self.study.trials),
                'n_completed_trials': n_completed_trials,
                'n_pruned_trials': n_pruned_trials,
                'n_failed_trials': n_failed_trials
            },
            'performance_statistics': performance_stats,
            'parameter_importance': param_importance,
            'trial_duration_statistics': duration_stats,
            'optimization_timestamp': datetime.now().isoformat()
        }
        
        return report
    
    def _save_optimization_results(self, report: Dict[str, Any]):
        """Save optimization results"""
        try:
            # Create results directory
            results_dir = Path("mlops/optimization_results")
            results_dir.mkdir(parents=True, exist_ok=True)
            
            # Save detailed report
            report_file = results_dir / f"{self.config.study_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            # Save best parameters separately for easy access
            best_params_file = results_dir / f"{self.config.study_name}_best_params.json"
            with open(best_params_file, 'w') as f:
                json.dump(report['results']['best_params'], f, indent=2)
            
            # Save study object for later analysis
            study_file = results_dir / f"{self.config.study_name}_study.joblib"
            joblib.dump(self.study, study_file)
            
            logger.info(f"💾 Optimization results saved: {report_file}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save optimization results: {e}")


def create_default_hyperparameter_space() -> HyperparameterSpace:
    """Create default hyperparameter space for DAGnostics"""
    return HyperparameterSpace(
        learning_rate_min=1e-6,
        learning_rate_max=1e-3,
        batch_sizes=[1, 2, 4],  # CPU-friendly batch sizes
        epochs_min=1,
        epochs_max=5,
        max_length_options=[256, 512],  # Reasonable for error extraction
        optimizer_choices=["adamw_torch", "adafactor"],
        lora_r_options=[4, 8, 16],
        lora_alpha_options=[8, 16, 32]
    )


def create_cpu_optimized_config(study_name: str) -> OptimizationConfig:
    """Create CPU-optimized configuration"""
    return OptimizationConfig(
        study_name=study_name,
        n_trials=10,  # Fewer trials for CPU
        timeout=7200,  # 2 hours max
        metric_name="val_loss",
        direction="minimize",
        max_epochs_per_trial=3,  # Shorter epochs for CPU
        max_time_per_trial=1800,  # 30 minutes per trial
        early_stopping_patience=3
    )


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    def dummy_training_function(params: Dict[str, Any]) -> float:
        """Dummy training function for testing"""
        # Simulate training with some noise
        lr = params['learning_rate']
        epochs = params['epochs']
        batch_size = params['batch_size']
        
        # Simulate that lower learning rate and more epochs = better performance
        simulated_loss = 10.0 - (np.log10(lr) * -0.5) - (epochs * 0.3) + np.random.normal(0, 0.1)
        simulated_loss += (batch_size - 2) * 0.1  # Slight penalty for larger batch sizes
        
        return max(0.1, simulated_loss)  # Ensure positive loss
    
    # Setup optimization
    space = create_default_hyperparameter_space()
    config = create_cpu_optimized_config("test-optimization")
    
    tuner = HyperparameterTuner(config, space, dummy_training_function)
    
    # Run optimization
    results = tuner.optimize()
    
    print(f"🏆 Best parameters: {results['best_params']}")
    print(f"📊 Best value: {results['best_value']:.4f}")
    
    # Generate plots
    tuner.plot_optimization_history()
    
    print("✅ Hyperparameter optimization system ready!")