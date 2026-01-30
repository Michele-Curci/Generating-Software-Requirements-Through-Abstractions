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
* The **Original Dataset** (250 requirements), which is much noisier and inconsistent.

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
    

#Sharhzad
#Structure

