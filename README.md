# Generating-Software-Requirements-Through-Abstractions
Repository for the project of the course "Large language models for software engineering"
---------------------------------------------------------------------------------------------------------------------

Assignment description:\n
Requirements are often ambiguous, inconsistent, and nonstandardized. LLMs can support requirement authoring, but they still risk to misinterpret human needs. For this reason, a more systematic approach, based on the clear identification of the requirements’ building blocks, may prove benefits.

Can LLMs reliably identify the different abstraction that compose a requirement (e.g., the main actor, the system response, the precondition…)?\n
Does this analysis improve requirements’ clarity and completeness?\n
Can LLMs manage nested items?\n

Requirement Dataset: Choose 30+ requirements from any of the following:
- past course assignments
- open-source software requirement documents
- your own small system description
Each requirement must be realistic and contain multiple semantic components (e.g.,
actions, conditions, constraints).

System Implementation. Include:
- One single-agent baseline→ An LLM generates requirements or annotates them directly.
- One multi-step or multi-agent workflow that performs semantic decomposition into ≥4 tags

Evaluation. Use at least one of the following evaluation methods:
- annotation accuracy against a small human-created gold standard
- clarity and completeness comparison between flat vs structured outputs
- consistency checking (e.g., detecting contradictions or missing components) <- this is applicable only if the starting requirements are very high quality
