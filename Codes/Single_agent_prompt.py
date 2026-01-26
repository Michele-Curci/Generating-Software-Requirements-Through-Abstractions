#Base instructions common to all prompts
BASE_INSTRUCTIONS = """You are an expert Requirements Engineer specialized in Requirements Modeling.
Your task is to transform a software requirement into a structured JSON abstraction.

### EXTRACTION RULES:
Extract all relevant substrings exactly as they appear in the text. Return each field as a LIST of strings.
If a component is not present, return an empty list [].

1. "Purpose": The reason why the functionality described by the software requirement needs to be implemented.
2. "Trigger": An event establishing a temporal context and a causal link that constrains the requirement's applicability. A trigger is also a condition.
3. "Condition": Something that limits the scope of application of the requirement.
4. "Precondition": A condition that must hold in the requirement's context. A precondition is always a condition.
5. "Main_actor": The main user of the functionality described by the requirement. The main actor is often also an entity. The main actor is who gets the advantages of the requirement, not the grammatical subject
of the requirement.
6. "Entity": Something involved in the actions described in the requirement. Can be both human or not (e.g. the system).
7. "Action": Something that happens in the scenario described by the software requirement.
8. "System_response": The behaviour of the system in the described scenario. A system response is always an action.

### FORMATTING RULES:
- Return ONLY a valid JSON object.
- Every value MUST be a LIST of strings.
- Do NOT add markdown code blocks (no ```json).
- Extract substrings EXACTLY. Do not paraphrase.

JSON STRUCTURE:
{
  "abstractions": [
    {
      "Purpose": [], "Trigger": [], "Condition": [], "Precondition": [],
      "Main_actor": [], "Entity": [], "Action": [], "System_response": []
    }
  ]
}"""

# Examples to use for One-Shot and Few-Shot
EXAMPLE_1 = """Requirement: When the offensive player takes a shot the product shall simulate the sound of a ship at sea.
JSON: {
  "abstractions": [{
    "Purpose": [],
    "Trigger": ["When the offensive player takes a shot"],
    "Condition": ["When the offensive player takes a shot"],
    "Precondition": [],
    "Main_actor": ["the offensive player"],
    "Entity": ["offensive player", "the product", "a shot", "sound of a ship at sea"],
    "Action": ["takes", "simulate"],
    "System_response": ["simulate the sound of a ship at sea"]
  }]
}"""

EXAMPLE_2 = """Requirement: The system will return to the user the report of his actions every 2 minutes.
JSON: {
  "abstractions": [{
    "Purpose": ["The system will return to the user the report of his action every 2 minutes"],
    "Trigger": ["every 2 minutes"],
    "Condition": ["every 2 minutes","of his actions"],
    "Precondition": [],
    "Main_actor": ["The user"],
    "Entity": ["The system", "the user", "the report"],
    "Action": ["will return"],
    "System_response": ["will return"]
  }]
}"""


EXAMPLE_3 = """Requirement: The system shall be available 99% of the time during business hours.
JSON: {
  "abstractions": [{
    "Purpose": [],
    "Trigger": [],
    "Condition": ["during business hours"],
    "Precondition": ["99% of the time", "during business hours"],
    "Main_actor": [],
    "Entity": ["The system"],
    "Action": ["shall be available"],
    "System_response": ["shall be available"]
  }]
}"""

# The Dictionary of Prompts
PROMPT_VARIANTS = {
    "zero_shot": BASE_INSTRUCTIONS,

    "one_shot": f"{BASE_INSTRUCTIONS}\n\n### EXAMPLE:\n{EXAMPLE_1}",

    "few_shot": f"{BASE_INSTRUCTIONS}\n\n### EXAMPLES:\n{EXAMPLE_1}\n\n{EXAMPLE_2}\\{EXAMPLE_3}"
}