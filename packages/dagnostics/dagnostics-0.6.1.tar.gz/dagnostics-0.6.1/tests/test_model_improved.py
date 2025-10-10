#!/usr/bin/env python3
"""
Improved model testing script for DAGnostics fine-tuned model
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def test_model():
    # Use your actual model path
    model_path = "models/fine_tuned/remote-train_1755498878-20250818-064923/"
    
    print("🔄 Loading model and tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path)
    
    # Set pad token to avoid warnings
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    print("✅ Model loaded successfully!")
    print(f"📊 Model info: {model.config.name_or_path}")
    print(f"🔤 Vocab size: {tokenizer.vocab_size}")
    
    # Test cases in the format the model was trained on
    test_cases = [
        {
            "input": "Analyze the following Airflow task failure log and extract the primary error.\n\nInput: [2025-08-18T10:01:00.000+0600] {logging_mixin.py:190} INFO - BTEQ command exited with return code 45\n[2025-08-18T10:01:00.100+0600] {standard_task_runner.py:124} ERROR - Failed to execute job 67890\n\nOutput:",
            "expected": "BTEQ command exited with return code 45"
        },
        {
            "input": "Analyze the following Airflow task failure log and extract the primary error.\n\nInput: [2025-08-17T10:02:00.000+0600] {logging_mixin.py:190} INFO - mget: Access failed: No such file (DATA_20250817.csv)\n[2025-08-17T10:02:00.200+0600] {standard_task_runner.py:124} ERROR - Failed to execute job 11111\n\nOutput:",
            "expected": "mget: Access failed: No such file (DATA_20250817.csv)"
        },
        {
            "input": "Analyze the following Airflow task failure log and extract the primary error.\n\nInput: [2025-08-17T10:04:00.000+0600] {subprocess.py:93} INFO - ls: write error: No space left on device\n[2025-08-17T10:04:00.200+0600] {standard_task_runner.py:124} ERROR - Failed to execute job 33333\n\nOutput:",
            "expected": "ls: write error: No space left on device"
        }
    ]
    
    print("\n" + "="*80)
    print("🧪 TESTING MODEL PERFORMANCE")
    print("="*80)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Expected: {test_case['expected']}")
        
        # Tokenize with proper attention mask
        inputs = tokenizer(
            test_case['input'], 
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        )
        
        # Generate response with better parameters
        with torch.no_grad():
            outputs = model.generate(
                inputs['input_ids'],
                attention_mask=inputs['attention_mask'],
                max_new_tokens=50,  # Only generate 50 new tokens
                do_sample=True,
                temperature=0.3,  # Lower temperature for more focused output
                top_p=0.9,
                top_k=50,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                repetition_penalty=1.1
            )
        
        # Decode only the generated part
        generated_tokens = outputs[0][len(inputs['input_ids'][0]):]
        generated_text = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()
        
        print(f"Generated: {generated_text}")
        
        # Simple evaluation
        if test_case['expected'].lower() in generated_text.lower():
            print("✅ PASS - Contains expected error")
        else:
            print("❌ FAIL - Does not contain expected error")
        
        print("-" * 50)
    
    # Interactive testing
    print("\n" + "="*80)
    print("🎮 INTERACTIVE TESTING")
    print("="*80)
    print("Enter your own error logs to test (or 'quit' to exit):")
    
    while True:
        user_input = input("\nEnter error log: ").strip()
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
            
        if not user_input:
            continue
            
        # Format the input properly
        formatted_input = f"Analyze the following Airflow task failure log and extract the primary error.\n\nInput: {user_input}\n\nOutput:"
        
        inputs = tokenizer(
            formatted_input,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        )
        
        with torch.no_grad():
            outputs = model.generate(
                inputs['input_ids'],
                attention_mask=inputs['attention_mask'],
                max_new_tokens=30,
                do_sample=False,  # Deterministic for consistency
                temperature=0.1,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )
        
        generated_tokens = outputs[0][len(inputs['input_ids'][0]):]
        generated_text = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()
        
        print(f"🎯 Extracted Error: {generated_text}")

if __name__ == "__main__":
    test_model()