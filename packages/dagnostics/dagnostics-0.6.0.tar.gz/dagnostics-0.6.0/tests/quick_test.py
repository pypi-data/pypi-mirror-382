from transformers import AutoTokenizer, AutoModelForCausalLM

model_path = "models/fine_tuned/remote-train_1755498878-20250818-064923/"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path)

# Set pad token
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

# Test the exact training format
prompt = """Analyze the following Airflow task failure log and extract the primary error.

Input: [2025-08-18T10:01:00.000+0600] {logging_mixin.py:190} INFO - BTEQ command exited with return code 45

Output:"""

inputs = tokenizer(prompt, return_tensors="pt", padding=True)

# Generate with minimal parameters
outputs = model.generate(
    inputs['input_ids'],
    attention_mask=inputs['attention_mask'],
    max_new_tokens=20,
    do_sample=False,
    pad_token_id=tokenizer.eos_token_id
)

# Get only the generated part
generated_tokens = outputs[0][len(inputs['input_ids'][0]):]
result = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()

print(f"Input: BTEQ command exited with return code 45")
print(f"Model output: '{result}'")
print(f"Success: {'BTEQ' in result or 'return code 45' in result or '45' in result}")