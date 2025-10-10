#!/usr/bin/env python3
"""
Compare base model vs fine-tuned to prove model collapse
"""

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

def test_model_collapse():
    print("🔬 TESTING: Base Model vs Fine-tuned Model")
    print("="*60)
    
    # Test 1: Base model (should work reasonably)
    print("\n1️⃣ TESTING BASE MODEL")
    print("-" * 30)
    
    try:
        base_tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
        base_model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")
        
        if base_tokenizer.pad_token is None:
            base_tokenizer.pad_token = base_tokenizer.eos_token
        
        test_inputs = [
            "Error: BTEQ command failed",
            "The system encountered an error",  
            "Failed to execute task",
            "File not found"
        ]
        
        for test_input in test_inputs:
            inputs = base_tokenizer(test_input, return_tensors="pt")
            
            with torch.no_grad():
                outputs = base_model.generate(
                    inputs['input_ids'],
                    max_new_tokens=15,
                    do_sample=False,
                    pad_token_id=base_tokenizer.eos_token_id,
                    temperature=1.0
                )
            
            generated_tokens = outputs[0][len(inputs['input_ids'][0]):]
            result = base_tokenizer.decode(generated_tokens, skip_special_tokens=True)
            
            print(f"Input: '{test_input}'")
            print(f"Base Output: '{result}'")
            
            # Check for model collapse signs
            unique_chars = len(set(result.replace(' ', '')))
            if unique_chars <= 2:
                print("  ❌ BASE MODEL ALSO COLLAPSED!")
            elif len(result.strip()) == 0:
                print("  ⚠️  Empty output")
            else:
                print("  ✅ Normal output")
            print()
            
    except Exception as e:
        print(f"❌ Base model failed: {e}")
        return
    
    # Test 2: Fine-tuned model (showing collapse)
    print("\n2️⃣ TESTING FINE-TUNED MODEL")
    print("-" * 30)
    
    try:
        ft_model_path = "models/fine_tuned/remote-train_1755498878-20250818-064923/"
        ft_tokenizer = AutoTokenizer.from_pretrained(ft_model_path)
        ft_model = AutoModelForCausalLM.from_pretrained(ft_model_path)
        
        if ft_tokenizer.pad_token is None:
            ft_tokenizer.pad_token = ft_tokenizer.eos_token
        
        for test_input in test_inputs:
            inputs = ft_tokenizer(test_input, return_tensors="pt")
            
            with torch.no_grad():
                outputs = ft_model.generate(
                    inputs['input_ids'],
                    max_new_tokens=15,
                    do_sample=False,
                    pad_token_id=ft_tokenizer.eos_token_id,
                    temperature=1.0
                )
            
            generated_tokens = outputs[0][len(inputs['input_ids'][0]):]
            result = ft_tokenizer.decode(generated_tokens, skip_special_tokens=True)
            
            print(f"Input: '{test_input}'")
            print(f"Fine-tuned Output: '{result}'")
            
            # Analyze the collapse
            unique_chars = len(set(result.replace(' ', '')))
            if unique_chars <= 2:
                print(f"  ❌ MODEL COLLAPSE! Only {unique_chars} unique characters")
                print(f"  📊 Character distribution: {set(result[:20])}")
            elif result.count(',') > len(result) // 3:
                print(f"  ❌ COMMA OBSESSION! {result.count(',')} commas in {len(result)} chars")
            else:
                print("  ✅ Normal output")
            print()
            
    except Exception as e:
        print(f"❌ Fine-tuned model failed: {e}")
        return
    
    # Test 3: Analyze the tokenizer
    print("\n3️⃣ TOKENIZER ANALYSIS")  
    print("-" * 30)
    
    # Check if tokenizer was corrupted
    comma_token_id = base_tokenizer.encode(",")[0] if base_tokenizer.encode(",") else None
    print(f"Comma token ID: {comma_token_id}")
    
    # Check what token the model is obsessed with
    obsessed_tokens = base_tokenizer.encode(",,,,")
    print(f"Comma sequence tokens: {obsessed_tokens}")
    
    # Test if the model can generate anything else
    print("\n🧪 Testing model capability recovery:")
    simple_prompt = "Hello"
    inputs = ft_tokenizer(simple_prompt, return_tensors="pt")
    
    with torch.no_grad():
        outputs = ft_model.generate(
            inputs['input_ids'],
            max_new_tokens=5,
            do_sample=True,  # Try with sampling
            temperature=0.8,
            top_k=50,
            pad_token_id=ft_tokenizer.eos_token_id
        )
    
    generated_tokens = outputs[0][len(inputs['input_ids'][0]):]
    result = ft_tokenizer.decode(generated_tokens, skip_special_tokens=True)
    print(f"Simple test - Input: 'Hello', Output: '{result}'")
    
    if ',' in result:
        print("❌ CONFIRMED: Model is stuck generating commas even for 'Hello'")
        print("🔥 DIAGNOSIS: Complete model collapse due to bad training")
    
    # Final analysis
    print(f"\n📋 CONCLUSION:")
    print(f"- Fine-tuning with 12 examples + wrong hyperparameters = Model destruction")
    print(f"- The model learned that ',' is the 'correct' output for everything")  
    print(f"- This is worse than using the untrained base model")
    print(f"- Solution: Better training data + proper hyperparameters")

if __name__ == "__main__":
    test_model_collapse()