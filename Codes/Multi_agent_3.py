import torch
import json
import re
from tqdm import tqdm
import time
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    pipeline
)

from huggingface_hub import login
from Multi_agent_3prompt import AGENT_ENTITY_PROMPT, AGENT_ACTION_PROMPT, AGENT_LOGIC_PROMPT

HF_TOKEN = '< YOUR TOKEN >'

MODEL_ID = "meta-llama/Meta-Llama-3.1-8B-Instruct"
INPUT_FILE = 'requirements.json'
OUTPUT_FILE = "llama3_output.json"
login(token=HF_TOKEN)

def load_model():
    '''
    Load the LLaMA 3 model in 4-bit quantization.
    '''
    print(f"Loading {MODEL_ID} in 4-bit...")
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
        token=HF_TOKEN)

    return pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=1024,
        do_sample=False,
        return_full_text=False)

def query_llm(pipe, messages):
    """Invia i messaggi al modello e ritorna la risposta testuale."""
    output = pipe(messages)
    return output[0]['generated_text'].strip()

def extract_clean_json(text_output):
    """
    Extracts and parses the first valid JSON object found in a text string.
    Handles Markdown blocks, introductory text, and parsing errors.
    """
    try:
        if not text_output:
            return {}

        # 1. Find the index of the first opening brace '{'
        start_idx = text_output.find('{')

        # 2. Find the index of the last closing brace '}'
        end_idx = text_output.rfind('}')

        # If braces are not found, return empty (or handle error as needed)
        if start_idx == -1 or end_idx == -1:
            # Optional: print a warning for debug purposes
            # print(f"Warning: No JSON braces found in: {text_output[:50]}...")
            return {}

        # 3. Extract only the substring containing the JSON
        # We add +1 to end_idx to include the closing brace itself
        json_str = text_output[start_idx : end_idx + 1]

        # 4. Safe Parsing
        data = json.loads(json_str)
        return data

    except json.JSONDecodeError as e:
        print(f"JSON Decoding Error: {e}")
        # Print part of the text to understand what went wrong
        print(f"   Problematic text: {text_output[:100]}...")
        return {}

    except Exception as e:
        print(f"Unexpected Error: {e}")
        return {}
    
# --- SMART FILTER (Deduplication + Atomic Protection) ---
def smart_filter(string_list):
    """
    Removes redundant substrings but PROTECTS atomic values.
    Rule: Delete string A if it is inside string B, UNLESS A contains a digit
    and is short (e.g., '99%' or '10x10'), in which case keep it.
    """
    if not string_list: return []

    # Sort by length (descending) to check longest phrases first
    unique = sorted(list(set(string_list)), key=len, reverse=True)
    final = []

    for candidate in unique:
        is_substring = False
        for other in unique:
            if candidate != other and candidate in other:
                is_substring = True
                break

        # If it's unique, keep it. If it's a substring, check for "Atomic Protection"
        if not is_substring:
            final.append(candidate)

    return final

def process_requirements(req, id, pipe):
    """
    Runs the 3-Agent Pipeline: Entity -> Action -> Logic.
    Applies Mirror Rule, Hierarchy Rule, and Smart Filtering.
    """

    # Settings for deterministic output (Temp 0)
    gen_config = {"max_new_tokens": 500, "do_sample": False}


    # A. ENTITY AGENT
    msg1 = [{"role": "system", "content": AGENT_ENTITY_PROMPT},
            {"role": "user", "content": f"Input: \"{req}\""}]
    raw1 = pipe(msg1, **gen_config)[0]['generated_text']
    res_entity = extract_clean_json(raw1) or {"Main_actor": [], "Entity": []}

    # B. ACTION AGENT (Context Injection)
    context = f"Actors: {res_entity.get('Main_actor')}, Entities: {res_entity.get('Entity')}"
    msg2 = [{"role": "system", "content": AGENT_ACTION_PROMPT},
            {"role": "user", "content": f"Input Req: \"{req}\"\nContext: {context}"}]
    raw2 = pipe(msg2, **gen_config)[0]['generated_text']
    res_action = extract_clean_json(raw2) or {"Action": [], "System_response": [], "Purpose": []}

    # C. LOGIC AGENT (Contrastive)
    msg3 = [{"role": "system", "content": AGENT_LOGIC_PROMPT},
            {"role": "user", "content": f"Input: \"{req}\""}]
    raw3 = pipe(msg3, **gen_config)[0]['generated_text']
    res_logic = extract_clean_json(raw3) or {"Trigger": [], "Precondition": [], "Condition": []}



    all_entities = set(res_entity.get("Entity", [])) | set(res_entity.get("Main_actor", []))
    all_conditions = set(res_logic.get("Condition", [])) | set(res_logic.get("Trigger", [])) | set(res_logic.get("Precondition", []))

    # 3. Apply Smart Filter (Clean text, protect numbers)
    final_entry = {
        "id": id,
        "Text": req,
        # Entity Section
        "Main_actor": smart_filter(res_entity.get("Main_actor", [])),
        "Entity":     smart_filter(list(all_entities)),
        # Action Section
        "Action":          smart_filter(res_action.get("Action", [])),
        "System_response": smart_filter(res_action.get("System_response", [])),
        "Purpose":         smart_filter(res_action.get("Purpose", [])),
        # Logic Section
        "Trigger":      smart_filter(res_logic.get("Trigger", [])),
        "Precondition": smart_filter(res_logic.get("Precondition", [])),
        "Condition":    smart_filter(list(all_conditions))
    }

    return final_entry


# Load the model
try:
    pipe = load_model()
except Exception as e:
    print(f"Error with Model Loading: {e}")

    
results = []

with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    dataset = json.load(f)
    print(f"Processing {len(dataset)} requirements...")

    # --- Start Timer ---
    start_time = time.time()

    for entry in tqdm(dataset):
        req_text = entry.get("Text", "")
        req_id = entry.get("id", "unknown")
        prediction = process_requirements(req_text, req_id, pipe)

        results.append({
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