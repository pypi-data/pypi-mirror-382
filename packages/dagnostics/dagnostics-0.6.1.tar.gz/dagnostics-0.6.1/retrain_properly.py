#!/usr/bin/env python3
"""
Proper retraining with optimal parameters for CPU training
"""

import json
import sys
sys.path.insert(0, 'src')

from dagnostics.training.fine_tuner import train_from_prepared_data

def create_better_dataset():
    """Create a larger, higher-quality dataset"""
    
    # Expanded error patterns
    error_patterns = [
        # BTEQ/Teradata errors
        ("BTEQ command exited with return code 45", "BTEQ command exited with return code 45"),
        ("BTEQ command exited with return code 12", "BTEQ command exited with return code 12"),
        ("Transaction ABORTed due to Deadlock", "Transaction ABORTed due to Deadlock"),
        ("CREATE_TABLE:Transaction ABORTed due to Deadlock", "Transaction ABORTed due to Deadlock"),
        
        # File/Data errors  
        ("mget: Access failed: No such file (DATA_20250817.csv)", "mget: Access failed: No such file (DATA_20250817.csv)"),
        ("mget: Access failed: No such file (REPORT.txt)", "mget: Access failed: No such file (REPORT.txt)"),
        ("FileNotFoundError: [Errno 2] No such file or directory: 'data.csv'", "FileNotFoundError: [Errno 2] No such file or directory: 'data.csv'"),
        
        # System errors
        ("ls: write error: No space left on device", "ls: write error: No space left on device"),
        ("df: write error: No space left on device", "df: write error: No space left on device"),
        ("Permission denied: cannot access file", "Permission denied: cannot access file"),
        
        # TPT errors
        ("TPT Error: TPT_INFRA: TPT04183: Error: Line 1 of Command Line:", "TPT Error: TPT_INFRA: TPT04183: Error: Line 1 of Command Line:"),
        ("TPT Error: TPT_INFRA: TPT04184: Login failed", "TPT Error: TPT_INFRA: TPT04184: Login failed"),
        
        # Database connection errors
        ("Connection refused: unable to connect to database", "Connection refused: unable to connect to database"),
        ("Timeout: database connection timed out after 30s", "Timeout: database connection timed out after 30s"),
        ("Authentication failed for user 'airflow'", "Authentication failed for user 'airflow'"),
        
        # Memory/Resource errors
        ("OutOfMemoryError: Java heap space", "OutOfMemoryError: Java heap space"),
        ("MemoryError: Unable to allocate array", "MemoryError: Unable to allocate array"),
        ("CPU usage exceeded: task killed", "CPU usage exceeded: task killed"),
        
        # Network errors
        ("ConnectionError: HTTPSConnectionPool: Max retries exceeded", "ConnectionError: HTTPSConnectionPool: Max retries exceeded"),
        ("SSLError: certificate verify failed", "SSLError: certificate verify failed"),
        ("TimeoutError: Request timed out after 120 seconds", "TimeoutError: Request timed out after 120 seconds"),
    ]
    
    # Generate training examples
    train_examples = []
    val_examples = []
    
    for i, (error_log, expected_error) in enumerate(error_patterns):
        # Create realistic log context
        log_contexts = [
            f"[2025-08-18T10:{10+i:02d}:00.000+0600] {{taskinstance.py:1225}} INFO - Marking task as FAILED\n[2025-08-18T10:{10+i:02d}:00.100+0600] {{logging_mixin.py:190}} INFO - {error_log}\n[2025-08-18T10:{10+i:02d}:00.200+0600] {{standard_task_runner.py:124}} ERROR - Failed to execute job {67890+i}",
            
            f"[2025-08-18T11:{10+i:02d}:00.000+0600] {{subprocess.py:93}} INFO - {error_log}\n[2025-08-18T11:{10+i:02d}:00.100+0600] {{logging_mixin.py:190}} INFO - Command failed with exit code 1\n[2025-08-18T11:{10+i:02d}:00.200+0600] {{standard_task_runner.py:124}} ERROR - Task execution failed",
            
            f"[2025-08-18T12:{10+i:02d}:00.000+0600] {{logging_mixin.py:190}} INFO - Starting task execution\n[2025-08-18T12:{10+i:02d}:00.500+0600] {{logging_mixin.py:190}} ERROR - {error_log}\n[2025-08-18T12:{10+i:02d}:00.600+0600] {{taskinstance.py:1406}} ERROR - Task failed with error"
        ]
        
        # Create multiple examples per error pattern
        for j, context in enumerate(log_contexts):
            example = {
                "instruction": "Analyze the following Airflow task failure log and extract the primary error.",
                "input": context,
                "output": expected_error
            }
            
            # Split train/val (80/20)
            if (i * 3 + j) % 5 == 0:
                val_examples.append(example)
            else:
                train_examples.append(example)
    
    print(f"✅ Created {len(train_examples)} training examples")
    print(f"✅ Created {len(val_examples)} validation examples")
    
    # Save datasets
    with open('data/training/train_dataset.jsonl', 'w') as f:
        for example in train_examples:
            f.write(json.dumps(example) + '\n')
    
    with open('data/training/validation_dataset.jsonl', 'w') as f:
        for example in val_examples:
            f.write(json.dumps(example) + '\n')
    
    return len(train_examples), len(val_examples)

def retrain_with_optimal_params():
    """Retrain with optimal parameters for CPU"""
    
    print("🔄 Creating improved dataset...")
    train_size, val_size = create_better_dataset()
    
    print(f"🚀 Starting proper training with {train_size} examples...")
    
    # Optimal parameters for CPU training
    model_path = train_from_prepared_data(
        model_name="microsoft/DialoGPT-small",  # Keep same base model
        train_dataset_path="data/training/train_dataset.jsonl",
        validation_dataset_path="data/training/validation_dataset.jsonl",
        epochs=3,  # More epochs
        learning_rate=5e-6,  # Much lower learning rate for stability
        batch_size=1,  # Small batch for CPU
        model_output_name="dagnostics-fixed-cpu",
        use_quantization=False,  # No quantization for CPU
        export_for_ollama=False,  # Skip export
        force_cpu=True
    )
    
    print(f"🎉 Training completed! Model saved to: {model_path}")
    return model_path

if __name__ == "__main__":
    print("🎯 RETRAINING WITH PROPER PARAMETERS")
    print("="*50)
    
    # Ensure directories exist
    from pathlib import Path
    Path("data/training").mkdir(parents=True, exist_ok=True)
    
    model_path = retrain_with_optimal_params()
    print(f"\n✅ New model ready for testing: {model_path}")