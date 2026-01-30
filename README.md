# Generating Software Requirements Through Abstractions

**Course:** Large Language Models for Software Engineering (2025/2026)
**Project ID:** A3 - Minimum Requirements (Extraction & Semantic Analysis)

---------------------------------------------------------------------------------------------------------------------

## Introduction

This repository contains the code and experiments for our group project regarding the automation of requirements engineering. The main idea was to see if we could use Large Language Models (LLMs) to transform unstructured natural language text into structured specifications—specifically identifying *Actors*, *Actions*, *Conditions*, and *Entities*—without doing it manually.

We worked primarily with the **Meta-Llama-3-8B-Instruct** model. Since we had computational constraints (we ran most tests on free Colab T4 instances), we used the 4-bit quantized version for all our experiments.

### What we did
The goal wasn't just to get the highest accuracy, but to compare different architectural approaches to see which one is more robust when dealing with real-world, "messy" data.

We implemented and compared three main strategies:
1.  **Baselines:** Standard Zero-shot, One-shot, and Few-shot prompting.
2.  **SCAP (Sequential Context-Aware Pipeline):** A multi-agent approach where 3 agents work in a chain (Entity $\to$ Action $\to$ Logic), passing context to each other to maintain coherence.
3.  **MIA (Modular Independent Agents):** A parallel approach with 8 specialized agents, designed to find as much information as possible (high recall), even if it means generating more noise.

### Evaluation & Data
We tested these models on two datasets:
* A **Cleaned Dataset** (50 requirements) that acts as our manually verified Gold Standard.
* The **Original Dataset** (250 requirements), which is much noisier and more inconsistent.

For the evaluation, we realized that simple string matching wasn't fair because LLMs often paraphrase correctly. So, instead of standard accuracy, we wrote a script using **SBERT** (Sentence-BERT) to check semantic similarity between the extraction and the ground truth.

### Main Findings
As detailed in our report, we found an interesting trade-off: simple models (like One-shot) work great if the data is perfect, but they fail when the data is noisy. The Multi-Agent approaches (especially SCAP) are slower (about 30% more latency) but proved to be much more robust and reliable in real-world scenarios.

---------------------------------------------------------------------------------------------------------------------

## *The Dataset directory is divided into:*
- Dataset_250, containing 250 dirty requirements
- Dataset_50, containing the 50 cleaned requirements. 

Each directory contains the source Dataset file in JSON format and the results obtained by each agentic pipeline (zero_shot, one_shot, few_shot, MultiAgent, MultiAgent1).

```text
Dataset/
├── Dataset_250/
│   ├── requirements.json
│   └── [pipeline_results].json
└── Dataset_50/
    ├── cleaned_requirements_final.json
    └── [pipeline_results].json
```
    

---------------------------------------------------------------------------------------------------------------------

## Code Structure & File Descriptions

Here's a quick breakdown of what each file in the `Codes/` folder does. We tried to keep things modular, so it's easier to understand and modify.

### Inference Scripts (The Main Pipelines)

| File | What it does |
|------|--------------|
| **`Single_agent.py`** | This is our baseline script. It loads the Llama 3 model (4-bit quantized) and runs inference using a single prompt. You can switch between zero-shot, one-shot, and few-shot just by changing the `strategy` variable. It reads requirements from a JSON file, sends each one to the LLM, parses the JSON output, and saves everything to a results file. Pretty straightforward. |
| **`Multi_agent_3.py`** | This is our **SCAP (Sequential Context-Aware Pipeline)**. Instead of one big prompt, we use 3 specialized agents that work in a chain: **Entity Agent → Action Agent → Logic Agent**. The cool part is that each agent passes its output to the next one as context, so they build on each other's work. We also added a `smart_filter()` function to clean up duplicate extractions. |
| **`Multi_agent_8.py`** | This is our **MIA (Modular Independent Agents)** approach. Here we have 8 separate agents, one for each extraction field (Purpose, Trigger, Condition, etc.). They all run independently (no context sharing), which makes it more like a "high recall" strategy—we extract as much as possible, even if there's some noise. |

### Prompt Files (The Brains Behind the Agents)

| File | What it does |
|------|--------------|
| **`Single_agent_prompt.py`** | Contains all the prompts for the single-agent baselines. We defined a `BASE_INSTRUCTIONS` string with the extraction rules, and then created variants for zero-shot (just the base), one-shot (base + 1 example), and few-shot (base + 3 examples). The examples were carefully picked to cover different requirement types. |
| **`Multi_agent_3prompt.py`** | Holds the prompts for our 3-agent pipeline. Each agent has its own specialized prompt: `AGENT_ENTITY_PROMPT` focuses on actors/entities, `AGENT_ACTION_PROMPT` handles verbs and system responses, and `AGENT_LOGIC_PROMPT` extracts conditions/triggers. We added contrastive examples to help the LLM distinguish between static and dynamic requirements. |
| **`Multi_agent_8prompt.py`** | Contains 8 mini-prompts, one per extraction field. They all share a common `SHARED_RULES` base, but each one is laser-focused on extracting just one thing (e.g., only "Trigger", only "Entity"). This keeps each prompt simple and reduces confusion for the model. |

### Evaluation

| File | What it does |
|------|--------------|
| **`Evaluation.ipynb`** | This is our main evaluation notebook (runs on Colab). It does a lot: loads ground truth and predictions, computes precision/recall/F1 using **SBERT semantic similarity** (not just exact string matching), finds the optimal similarity threshold, generates comparison charts, builds confusion matrices, and exports everything to nice visualizations. We also added qualitative error analysis to manually inspect hallucinations and omissions. |

### How Everything Connects

```
┌─────────────────────────────────────────────────────────────────┐
│                        INFERENCE PHASE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   requirements.json ──► Single_agent.py ──► predictions.json   │
│                              │                                  │
│                              ▼                                  │
│                    Single_agent_prompt.py                       │
│                    (zero/one/few-shot)                          │
│                                                                 │
│   requirements.json ──► Multi_agent_3.py ──► predictions.json  │
│                              │                                  │
│                              ▼                                  │
│                    Multi_agent_3prompt.py                       │
│                    (Entity→Action→Logic)                        │
│                                                                 │
│   requirements.json ──► Multi_agent_8.py ──► predictions.json  │
│                              │                                  │
│                              ▼                                  │
│                    Multi_agent_8prompt.py                       │
│                    (8 parallel agents)                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       EVALUATION PHASE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ground_truth.json + predictions.json                          │
│              │                                                  │
│              ▼                                                  │
│      Evaluation.ipynb                                           │
│              │                                                  │
│              ▼                                                  │
│   ┌─────────────────────────────────────┐                       │
│   │ • Semantic matching (SBERT)         │                       │
│   │ • Threshold optimization            │                       │
│   │ • Precision/Recall/F1 scores        │                       │
│   │ • Confusion matrices                │                       │
│   │ • Error analysis reports            │                       │
│   └─────────────────────────────────────┘                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Quick Notes
- All scripts use **4-bit quantization** (`BitsAndBytesConfig`) to fit the model on a free Colab T4 GPU.
- You'll need to add your own HuggingFace token where it says `'< YOUR TOKEN >'`.
- The `smart_filter()` function in Multi_agent_3.py removes redundant substrings while protecting atomic values like percentages.
- We use `do_sample=False` for deterministic outputs (reproducibility).

