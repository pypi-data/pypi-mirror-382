#!/usr/bin/env python3
"""
Installation script for DAGnostics MLOps dependencies
"""

import subprocess
import sys
from pathlib import Path

def install_mlops_dependencies():
    """Install MLOps dependencies"""
    
    print("🚀 Installing DAGnostics MLOps Dependencies...")
    
    # Check if MLOps requirements file exists
    requirements_file = Path("mlops/requirements.txt")
    if not requirements_file.exists():
        print(f"❌ Requirements file not found: {requirements_file}")
        return False
    
    try:
        # Install MLOps requirements
        print("📦 Installing MLOps packages...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        
        # Create necessary directories
        print("📁 Creating MLOps directories...")
        directories = [
            "mlops",
            "mlops/experiments", 
            "mlops/data_reports",
            "mlops/models",
            "mlops/artifacts",
            "mlops/optimization_results",
            "mlops/pipeline_results",
            "mlops/logs"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        print("✅ MLOps dependencies installed successfully!")
        print("\n🎯 Next Steps:")
        print("1. Run MLOps training: uv run dagnostics training mlops")
        print("2. Enhanced remote training: uv run dagnostics training remote-train --enable-mlops")
        print("3. Direct MLOps CLI: uv run python -m mlops.cli train")
        print("4. View experiments: uv run python -m mlops.cli experiments")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = install_mlops_dependencies()
    sys.exit(0 if success else 1)