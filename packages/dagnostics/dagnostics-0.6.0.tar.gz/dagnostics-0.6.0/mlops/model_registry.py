#!/usr/bin/env python3
"""
MLOps Model Registry for DAGnostics
Advanced model versioning, registry, and lifecycle management
"""

import os
import shutil
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient

logger = logging.getLogger(__name__)


@dataclass
class ModelMetadata:
    """Model metadata for registry"""
    
    model_id: str
    version: str
    name: str
    description: str
    model_type: str  # "fine-tuned", "base", "quantized"
    base_model: str
    
    # Performance metrics
    metrics: Dict[str, float]
    
    # Training information
    training_dataset: str
    training_parameters: Dict[str, Any]
    training_duration_seconds: float
    
    # Model artifacts
    model_path: str
    model_size_mb: float
    model_hash: str
    
    # MLOps tracking
    experiment_id: str
    run_id: str
    
    # Lifecycle
    created_at: str
    created_by: str
    stage: str = "staging"  # staging, production, archived
    tags: Dict[str, str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}


@dataclass
class ModelComparisonResult:
    """Result of comparing two models"""
    
    model_a: str
    model_b: str
    comparison_metrics: Dict[str, Dict[str, float]]  # metric -> {model_a: val, model_b: val, diff: val}
    better_model: str
    improvement_summary: str
    comparison_timestamp: str


class ModelRegistry:
    """
    Advanced model registry for DAGnostics
    Handles model versioning, staging, and lifecycle management
    """
    
    def __init__(
        self,
        registry_path: str = "mlops/models",
        mlflow_tracking_uri: str = "sqlite:///mlops/experiments.db"
    ):
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)
        
        self.metadata_file = self.registry_path / "registry.json"
        self.models_dir = self.registry_path / "stored_models"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # MLflow integration
        mlflow.set_tracking_uri(mlflow_tracking_uri)
        self.mlflow_client = MlflowClient()
        
        # Load existing registry
        self.registry_data = self._load_registry()
        
        logger.info(f"🏛️  Model registry initialized: {self.registry_path}")
    
    def register_model(
        self,
        model_path: str,
        model_name: str,
        model_type: str = "fine-tuned",
        base_model: str = "microsoft/DialoGPT-small",
        description: str = "",
        metrics: Dict[str, float] = None,
        training_info: Dict[str, Any] = None,
        experiment_id: str = None,
        run_id: str = None,
        tags: Dict[str, str] = None
    ) -> ModelMetadata:
        """Register a new model in the registry"""
        
        logger.info(f"📝 Registering model: {model_name}")
        
        if not Path(model_path).exists():
            raise FileNotFoundError(f"Model path does not exist: {model_path}")
        
        # Generate model ID and version
        model_id = self._generate_model_id(model_name)
        version = self._get_next_version(model_name)
        
        # Calculate model hash and size
        model_hash = self._calculate_model_hash(model_path)
        model_size_mb = self._calculate_model_size(model_path)
        
        # Store model artifacts
        stored_model_path = self._store_model_artifacts(model_path, model_id, version)
        
        # Create metadata
        metadata = ModelMetadata(
            model_id=model_id,
            version=version,
            name=model_name,
            description=description or f"Fine-tuned {base_model} model",
            model_type=model_type,
            base_model=base_model,
            metrics=metrics or {},
            training_dataset=training_info.get('train_dataset_path', '') if training_info else '',
            training_parameters=training_info.get('parameters', {}) if training_info else {},
            training_duration_seconds=training_info.get('duration_seconds', 0) if training_info else 0,
            model_path=str(stored_model_path),
            model_size_mb=model_size_mb,
            model_hash=model_hash,
            experiment_id=experiment_id or '',
            run_id=run_id or '',
            created_at=datetime.now().isoformat(),
            created_by=os.getenv('USER', 'unknown'),
            tags=tags or {}
        )
        
        # Register in MLflow if tracking info available
        if experiment_id and run_id:
            try:
                self._register_in_mlflow(metadata)
            except Exception as e:
                logger.warning(f"Failed to register in MLflow: {e}")
        
        # Add to registry
        self.registry_data['models'][model_id] = asdict(metadata)
        self._save_registry()
        
        logger.info(f"✅ Model registered: {model_id} v{version}")
        
        return metadata
    
    def get_model(self, model_name: str, version: str = "latest") -> Optional[ModelMetadata]:
        """Get model metadata by name and version"""
        
        if version == "latest":
            model_id = self._get_latest_model_id(model_name)
        else:
            model_id = self._find_model_id(model_name, version)
        
        if not model_id:
            return None
        
        model_data = self.registry_data['models'].get(model_id)
        if not model_data:
            return None
        
        return ModelMetadata(**model_data)
    
    def list_models(self, stage: str = None, model_type: str = None) -> List[ModelMetadata]:
        """List all models with optional filtering"""
        
        models = []
        for model_data in self.registry_data['models'].values():
            metadata = ModelMetadata(**model_data)
            
            # Apply filters
            if stage and metadata.stage != stage:
                continue
            if model_type and metadata.model_type != model_type:
                continue
            
            models.append(metadata)
        
        # Sort by creation date (newest first)
        models.sort(key=lambda m: m.created_at, reverse=True)
        
        return models
    
    def promote_model(self, model_name: str, version: str, target_stage: str) -> bool:
        """Promote model to different stage (staging -> production)"""
        
        model = self.get_model(model_name, version)
        if not model:
            logger.error(f"Model not found: {model_name} v{version}")
            return False
        
        # Update stage
        self.registry_data['models'][model.model_id]['stage'] = target_stage
        self.registry_data['models'][model.model_id]['tags']['promoted_at'] = datetime.now().isoformat()
        
        self._save_registry()
        
        logger.info(f"🚀 Model promoted: {model_name} v{version} -> {target_stage}")
        
        return True
    
    def compare_models(
        self,
        model_a_name: str,
        model_b_name: str,
        model_a_version: str = "latest",
        model_b_version: str = "latest"
    ) -> Optional[ModelComparisonResult]:
        """Compare two models"""
        
        model_a = self.get_model(model_a_name, model_a_version)
        model_b = self.get_model(model_b_name, model_b_version)
        
        if not model_a or not model_b:
            logger.error("One or both models not found for comparison")
            return None
        
        # Compare metrics
        comparison_metrics = {}
        all_metrics = set(model_a.metrics.keys()) | set(model_b.metrics.keys())
        
        for metric in all_metrics:
            val_a = model_a.metrics.get(metric, float('inf'))
            val_b = model_b.metrics.get(metric, float('inf'))
            
            comparison_metrics[metric] = {
                f"{model_a_name}": val_a,
                f"{model_b_name}": val_b,
                "difference": val_b - val_a,
                "improvement_pct": ((val_b - val_a) / val_a * 100) if val_a != 0 else 0
            }
        
        # Determine better model (lower is better for loss/perplexity)
        primary_metric = "perplexity" if "perplexity" in comparison_metrics else list(comparison_metrics.keys())[0]
        
        if primary_metric in comparison_metrics:
            better_model = model_b_name if comparison_metrics[primary_metric]["difference"] < 0 else model_a_name
            improvement = abs(comparison_metrics[primary_metric]["improvement_pct"])
            improvement_summary = f"{better_model} is {improvement:.1f}% better on {primary_metric}"
        else:
            better_model = "inconclusive"
            improvement_summary = "No comparable metrics found"
        
        return ModelComparisonResult(
            model_a=f"{model_a_name} v{model_a.version}",
            model_b=f"{model_b_name} v{model_b.version}",
            comparison_metrics=comparison_metrics,
            better_model=better_model,
            improvement_summary=improvement_summary,
            comparison_timestamp=datetime.now().isoformat()
        )
    
    def get_production_model(self, model_name: str) -> Optional[ModelMetadata]:
        """Get the production version of a model"""
        
        for model_data in self.registry_data['models'].values():
            metadata = ModelMetadata(**model_data)
            if metadata.name == model_name and metadata.stage == "production":
                return metadata
        
        return None
    
    def archive_old_models(self, model_name: str, keep_latest: int = 5) -> int:
        """Archive old model versions, keeping only the latest N"""
        
        # Get all versions of the model
        model_versions = []
        for model_data in self.registry_data['models'].values():
            metadata = ModelMetadata(**model_data)
            if metadata.name == model_name:
                model_versions.append(metadata)
        
        # Sort by creation date (newest first)
        model_versions.sort(key=lambda m: m.created_at, reverse=True)
        
        # Archive old versions
        archived_count = 0
        for model in model_versions[keep_latest:]:
            if model.stage != "production":  # Never archive production models
                self.registry_data['models'][model.model_id]['stage'] = "archived"
                archived_count += 1
        
        if archived_count > 0:
            self._save_registry()
            logger.info(f"📦 Archived {archived_count} old model versions")
        
        return archived_count
    
    def delete_model(self, model_name: str, version: str) -> bool:
        """Delete a model from registry (use with caution!)"""
        
        model = self.get_model(model_name, version)
        if not model:
            logger.error(f"Model not found: {model_name} v{version}")
            return False
        
        if model.stage == "production":
            logger.error("Cannot delete production model")
            return False
        
        # Delete model artifacts
        try:
            if Path(model.model_path).exists():
                shutil.rmtree(model.model_path)
        except Exception as e:
            logger.warning(f"Failed to delete model artifacts: {e}")
        
        # Remove from registry
        del self.registry_data['models'][model.model_id]
        self._save_registry()
        
        logger.info(f"🗑️  Model deleted: {model_name} v{version}")
        
        return True
    
    def get_model_lineage(self, model_name: str, version: str = "latest") -> Dict[str, Any]:
        """Get model training lineage and provenance"""
        
        model = self.get_model(model_name, version)
        if not model:
            return {}
        
        lineage = {
            "model_info": asdict(model),
            "training_lineage": {
                "base_model": model.base_model,
                "training_dataset": model.training_dataset,
                "training_parameters": model.training_parameters,
                "training_duration": model.training_duration_seconds
            },
            "experiment_tracking": {
                "experiment_id": model.experiment_id,
                "run_id": model.run_id,
                "mlflow_uri": f"#/experiments/{model.experiment_id}/runs/{model.run_id}" if model.experiment_id else None
            },
            "model_artifacts": {
                "model_path": model.model_path,
                "model_size_mb": model.model_size_mb,
                "model_hash": model.model_hash
            }
        }
        
        return lineage
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load registry from file"""
        
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load registry: {e}")
        
        # Initialize empty registry
        return {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "models": {}
        }
    
    def _save_registry(self):
        """Save registry to file"""
        
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.registry_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save registry: {e}")
    
    def _generate_model_id(self, model_name: str) -> str:
        """Generate unique model ID"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{model_name}_{timestamp}"
    
    def _get_next_version(self, model_name: str) -> str:
        """Get next version number for model"""
        
        versions = []
        for model_data in self.registry_data['models'].values():
            if model_data['name'] == model_name:
                try:
                    version_num = int(model_data['version'])
                    versions.append(version_num)
                except ValueError:
                    pass
        
        next_version = max(versions) + 1 if versions else 1
        return str(next_version)
    
    def _get_latest_model_id(self, model_name: str) -> Optional[str]:
        """Get model ID of latest version"""
        
        latest_model = None
        latest_time = ""
        
        for model_id, model_data in self.registry_data['models'].items():
            if model_data['name'] == model_name and model_data['created_at'] > latest_time:
                latest_model = model_id
                latest_time = model_data['created_at']
        
        return latest_model
    
    def _find_model_id(self, model_name: str, version: str) -> Optional[str]:
        """Find model ID by name and version"""
        
        for model_id, model_data in self.registry_data['models'].items():
            if model_data['name'] == model_name and model_data['version'] == version:
                return model_id
        
        return None
    
    def _calculate_model_hash(self, model_path: str) -> str:
        """Calculate hash of model directory"""
        
        hasher = hashlib.sha256()
        model_path = Path(model_path)
        
        if model_path.is_file():
            with open(model_path, 'rb') as f:
                hasher.update(f.read())
        else:
            # Hash all files in directory
            for file_path in sorted(model_path.rglob('*')):
                if file_path.is_file():
                    with open(file_path, 'rb') as f:
                        hasher.update(f.read())
        
        return hasher.hexdigest()[:16]  # Short hash
    
    def _calculate_model_size(self, model_path: str) -> float:
        """Calculate model size in MB"""
        
        model_path = Path(model_path)
        total_size = 0
        
        if model_path.is_file():
            total_size = model_path.stat().st_size
        else:
            for file_path in model_path.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        
        return total_size / (1024 * 1024)  # Convert to MB
    
    def _store_model_artifacts(self, source_path: str, model_id: str, version: str) -> Path:
        """Store model artifacts in registry"""
        
        target_path = self.models_dir / f"{model_id}_v{version}"
        
        if Path(source_path).is_file():
            # Single file
            target_path.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, target_path / Path(source_path).name)
        else:
            # Directory
            if target_path.exists():
                shutil.rmtree(target_path)
            shutil.copytree(source_path, target_path)
        
        return target_path
    
    def _register_in_mlflow(self, metadata: ModelMetadata):
        """Register model in MLflow registry"""
        
        try:
            # Register model with MLflow
            model_uri = f"runs:/{metadata.run_id}/model"
            
            registered_model = mlflow.register_model(
                model_uri=model_uri,
                name=metadata.name,
                tags=metadata.tags
            )
            
            # Update model version in MLflow with metadata
            self.mlflow_client.update_model_version(
                name=metadata.name,
                version=registered_model.version,
                description=metadata.description
            )
            
            logger.info(f"📋 Registered in MLflow: {metadata.name} v{registered_model.version}")
            
        except Exception as e:
            logger.warning(f"MLflow registration failed: {e}")


def create_model_registry(registry_path: str = "mlops/models") -> ModelRegistry:
    """Create and initialize model registry"""
    
    return ModelRegistry(registry_path)


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Initialize registry
    registry = create_model_registry()
    
    # Example model registration (would be called from training pipeline)
    print("📝 Model Registry Example")
    print("Registry initialized and ready for model management")
    print("Available methods:")
    print("- register_model(): Register new model")
    print("- get_model(): Retrieve model metadata")
    print("- list_models(): List all models")
    print("- promote_model(): Promote to production")
    print("- compare_models(): Compare model performance")