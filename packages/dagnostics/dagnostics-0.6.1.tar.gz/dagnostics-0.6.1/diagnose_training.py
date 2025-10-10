#!/usr/bin/env python3
"""
Training diagnosis script - let's find out exactly what went wrong
"""

import json
import torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM

def diagnose_training():
    print("🔬 DIAGNOSING TRAINING ISSUES")
    print("="*60)
    
    # 1. Check training data quality
    print("\n1️⃣ TRAINING DATA ANALYSIS")
    print("-" * 30)
    
    train_file = "data/training/train_dataset.jsonl"
    val_file = "data/training/validation_dataset.jsonl"
    
    if not Path(train_file).exists():
        print(f"❌ Training file missing: {train_file}")
        return
    
    # Analyze training data
    examples = []
    with open(train_file, 'r') as f:
        for line in f:
            examples.append(json.loads(line.strip()))
    
    print(f"📊 Training examples: {len(examples)}")
    print(f"📊 First example keys: {list(examples[0].keys())}")
    
    # Check data quality
    for i, example in enumerate(examples[:3]):
        print(f"\n📝 Example {i+1}:")
        print(f"  Instruction: {example.get('instruction', 'MISSING')[:100]}...")
        print(f"  Input: {example.get('input', 'MISSING')[:100]}...")
        print(f"  Output: {example.get('output', 'MISSING')[:50]}...")
        
        # Check for problems
        if not example.get('output') or len(example.get('output', '')) < 5:
            print(f"  ⚠️  WARNING: Output too short or missing!")
        if not example.get('input') or len(example.get('input', '')) < 10:
            print(f"  ⚠️  WARNING: Input too short or missing!")
    
    # 2. Check model tokenization
    print(f"\n2️⃣ TOKENIZATION ANALYSIS")
    print("-" * 30)
    
    model_path = "models/fine_tuned/remote-train_1755498878-20250818-064923/"
    base_model = "microsoft/DialoGPT-small"
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        print("✅ Fine-tuned tokenizer loaded")
    except:
        print("❌ Fine-tuned tokenizer failed, trying base model")
        tokenizer = AutoTokenizer.from_pretrained(base_model)
    
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Test tokenization on training data
    example = examples[0]
    full_text = f"{example['instruction']}\n\nInput: {example['input']}\n\nOutput: {example['output']}"
    
    tokens = tokenizer.encode(full_text)
    print(f"📏 Example length: {len(tokens)} tokens")
    print(f"📏 Tokenizer vocab size: {tokenizer.vocab_size}")
    
    if len(tokens) > 1024:
        print("⚠️  WARNING: Example too long! Truncation happening!")
    
    # 3. Test model outputs
    print(f"\n3️⃣ MODEL OUTPUT ANALYSIS")
    print("-" * 30)
    
    try:
        model = AutoModelForCausalLM.from_pretrained(model_path)
        print("✅ Fine-tuned model loaded")
        
        # Test with different input lengths and formats
        test_prompts = [
            "Extract error:",  # Very short
            example['instruction'][:50],  # Medium
            full_text[:200],  # Longer
        ]
        
        for i, prompt in enumerate(test_prompts):
            print(f"\n🧪 Test {i+1}: '{prompt[:30]}...'")
            
            inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
            
            with torch.no_grad():
                outputs = model.generate(
                    inputs['input_ids'],
                    attention_mask=inputs.get('attention_mask'),
                    max_new_tokens=10,
                    do_sample=False,
                    temperature=1.0,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            generated_tokens = outputs[0][len(inputs['input_ids'][0]):]
            result = tokenizer.decode(generated_tokens, skip_special_tokens=True)
            print(f"   Output: '{result}'")
            print(f"   Length: {len(result)} chars")
            
            # Check if output is repetitive
            if len(set(result.replace(' ', ''))) <= 2:
                print("   ❌ REPETITIVE OUTPUT - Model collapsed!")
            elif not result.strip():
                print("   ❌ EMPTY OUTPUT - Model not generating!")
            elif len(result) < 3:
                print("   ❌ TOO SHORT - Model not learning!")
    
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
    
    # 4. Training parameter analysis
    print(f"\n4️⃣ TRAINING PARAMETERS ANALYSIS")
    print("-" * 30)
    
    print(f"📊 Dataset size: {len(examples)} examples")
    print(f"📊 Epochs: 1 (probably too few)")
    print(f"📊 Final loss: 19.377 (EXTREMELY HIGH)")
    print(f"📊 Training mode: CPU (much slower)")
    
    # Recommendations
    print(f"\n💡 SPECIFIC PROBLEMS IDENTIFIED:")
    print("-" * 30)
    
    if len(examples) < 50:
        print("❌ Dataset too small - need 100+ examples minimum")
    
    print("❌ Loss 19.377 indicates complete learning failure")
    print("❌ Only 1 epoch - need 3-5 epochs minimum")
    print("❌ CPU training severely limits model capacity")
    
    # Calculate optimal parameters
    print(f"\n🎯 RECOMMENDED FIXES:")
    print("-" * 30)
    print("1. Increase dataset to 200+ examples")
    print("2. Use 3-5 epochs instead of 1")
    print("3. Lower learning rate to 1e-5 or 5e-6")
    print("4. Increase batch size to 4-8 if possible")
    print("5. Use gradient accumulation for effective larger batches")
    print("6. Add more diverse error patterns")

if __name__ == "__main__":
    diagnose_training()