import torch
import json
import re
import os
from tqdm import tqdm
import time
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    Pipeline,
    pipeline
)
from huggingface_hub import login
from Multi_agent_8prompt import AGENT_PROMPTS


HF_TOKEN = '< YOUR TOKEN >'

MODEL_ID = "meta-llama/Meta-Llama-3.1-8B-Instruct"
INPUT_FILE = 'requirements.json'
OUTPUT_FILE = 'clean_multi_agent_predictions1.json'
login(token=HF_TOKEN)

def load_llama_model():
    '''
    Load the Llama 3 model with 4-bit quantization for efficient inference.
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

    print("Llama loaded")
    return text_pipe

def process_multi_agent_requirement(req_text, pipe, prompts_dict):
    """
    Orchestrates 8 separate calls to the model, one for each extraction field.
    """
    final_extraction = {}

    for field, prompt_template in prompts_dict.items():
        messages = [
            {"role": "system", "content": prompt_template},
            {"role": "user", "content": req_text}
        ]

        try:
            output = pipe(messages)
            # Accessing generated_text from Llama 3 format
            generated_text = output[0]['generated_text']

            # 1. Basic cleaning of markdown
            clean_text = generated_text.replace("```json", "").replace("```", "").strip()

            # 2. Extract JSON using regex (in case there is text before/after the { })
            json_match = re.search(r'\{.*\}', clean_text, re.DOTALL)
            if json_match:
                # 3. CONVERT string to dictionary
                data_dict = json.loads(json_match.group())

                # 4. Use .get() on the dictionary, not the string
                final_extraction[field] = data_dict.get(field, [])
            else:
                final_extraction[field] = []

        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON for {field}. Setting to empty list.")
            final_extraction[field] = []
        except Exception as e:
            print(f"Error in {field}: {str(e)}")
            final_extraction[field] = []

    return final_extraction

# Load the model
try:
    pipe = load_llama_model()
except Exception as e:
    print(f"Errore caricamento modello: {e}")
    print("Assicurati di aver accettato la licenza su HuggingFace e di avere il Token corretto.")

results = []

with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    dataset = json.load(f)
    print(f"Processing {len(dataset)} requirements...")

    # --- Start Timer ---
    start_time = time.time()

    for entry in tqdm(dataset):
        req_text = entry.get("Text", "")
        req_id = entry.get("id", "unknown")

        prediction = process_multi_agent_requirement(req_text, pipe, AGENT_PROMPTS)

        results.append({
          "id": req_id,
          "Text": req_text,
          **prediction
        })

    # --- End Timer ---
    end_time = time.time()
    total_duration = end_time - start_time

# Salvataggio
with open(OUTPUT_FILE, "w", encoding='utf-8') as f:
    json.dump(results, f, indent=4)

print("-" * 30)
print(f"Processing Complete!")
print(f"Total Time: {total_duration:.2f} seconds")
print(f"File saved in: {OUTPUT_FILE}")
print("-" * 30)