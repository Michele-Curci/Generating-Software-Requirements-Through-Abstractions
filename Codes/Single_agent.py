## Single agent inference script using LLaMA 3 model with 4-bit quantization.

import torch
import json
import os
from tqdm import tqdm
import time
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    pipeline
)
from huggingface_hub import login
from Single_agent_prompt import PROMPT_VARIANTS

HF_TOKEN = '< YOUR TOKEN >'

MODEL_ID = "meta-llama/Meta-Llama-3.1-8B-Instruct"
INPUT_FILE = 'Datasets/Dataset_250/requirements.json'
OUTPUT_FILE = 'one_shot_predictions.json'
login(token=HF_TOKEN)

def load_llama_model():
    '''
    Load the LLaMA 3 model with 4-bit quantization for inference.
    '''

    print(f"Load the {MODEL_ID} in 4-bit...")

    # 4-bit Quantization
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=HF_TOKEN)
    tokenizer.pad_token_id = tokenizer.eos_token_id

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        quantization_config=bnb_config,
        device_map="auto",
        token=HF_TOKEN
    )

    text_pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=512,
        #temperature=0.1,       # Low temperature for precision
        do_sample=False,       # Deterministic
        return_full_text=False
    )

    return text_pipe

def process_requirement(text, pipe):
    '''
    Process a single requirement text and return the extracted abstractions.
    '''

    strategy = "one_shot" # or "few_shot", "zero_shot"
    current_system_prompt = PROMPT_VARIANTS[strategy]
    messages = [
        {"role": "system", "content": current_system_prompt},
        {"role": "user", "content": text}
    ]

    try:
        output = pipe(messages)
        generated_text = output[0]['generated_text']

        clean_text = generated_text.replace("```json", "").replace("```", "").strip()
        # Parsing JSON
        return json.loads(clean_text)

    except json.JSONDecodeError:
        return {"error": "Invalid JSON", "raw_output": generated_text}
    except Exception as e:
        return {"error": str(e)}
    

# Load the model
try:
    pipe = load_llama_model()
except Exception as e:
    print(f"Error with Model Loading: {e}")

results = []

with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    dataset = json.load(f)

    # Timer Start
    start_time = time.time()

    # Process each requirement
    for entry in tqdm(dataset):
        req_text = entry.get("Text", "")
        req_id = entry.get("id", "unknown")
        prediction = process_requirement(req_text, pipe)

        if "abstractions" in prediction and len(prediction["abstractions"]) > 0:
          prediction_data = prediction["abstractions"][0]

        results.append({
        "id": req_id,
        "Text": req_text,
        **prediction_data
        })

    #End Timer
    end_time = time.time()
    total_duration = end_time - start_time

with open(OUTPUT_FILE, "w", encoding='utf-8') as f:
    json.dump(results, f, indent=4)

print("-" * 30)
print(f"Total Time: {total_duration:.2f} seconds")
print(f"File saved in: {OUTPUT_FILE}")
print("-" * 30)