# The common structure for all specialized agents
SHARED_RULES = """You are an expert Requirements Engineer.
Extract the substring EXACTLY as it appears in the text.
Return ONLY a valid JSON object. No markdown.
Every value MUST be a LIST of strings."""

# Dictionary of specialized agent prompts
# Dictionary of specialized agent prompts
AGENT_PROMPTS = {
    "Purpose": f"""{SHARED_RULES}
Task: Extract the "Purpose" (The reason why the functionality is implemented).
Example: "When the offensive player takes a shot the product shall simulate the sound of a ship at sea."
JSON: {{"Purpose": []}}

Requirement: {{text}}
JSON:""",

    "Trigger": f"""{SHARED_RULES}
Task: Extract the "Trigger" (Events establishing temporal context/causal link).
Example: "When the offensive player takes a shot the product shall simulate the sound of a ship at sea."
JSON: {{"Trigger": ["When the offensive player takes a shot"]}}

Requirement: {{text}}
JSON:""",

    "Condition": f"""{SHARED_RULES}
Task: Extract the "Condition" (Something that limits the scope of application).
Example: "When the offensive player takes a shot the product shall simulate the sound of a ship at sea."
JSON: {{"Condition": ["When the offensive player takes a shot"]}}

Requirement: {{text}}
JSON:""",

    "Precondition": f"""{SHARED_RULES}
Task: Extract the "Precondition" (A condition that must hold in the requirement's context).
Example: "The system shall be available 99% of the time during business hours."
JSON: {{"Precondition": ["99% of the time", "during business hours"]}}

Requirement: {{text}}
JSON:""",

    "Main_actor": f"""{SHARED_RULES}
Task: Extract the "Main_actor" (The main user or system initiating the functionality).
Example: "When the offensive player takes a shot the product shall simulate the sound of a ship at sea."
JSON: {{"Main_actor": ["the product"]}}

Requirement: {{text}}
JSON:""",

    "Entity": f"""{SHARED_RULES}
Task: Extract all "Entities" (Things involved in the actions, human or not).
Example: "When the offensive player takes a shot the product shall simulate the sound of a ship at sea."
JSON: {{"Entity": ["offensive player", "the product", "a shot", "sound of a ship at sea"]}}

Requirement: {{text}}
JSON:""",

    "Action": f"""{SHARED_RULES}
Task: Extract all "Actions" (Things that happen in the scenario).
Example: "When the offensive player takes a shot the product shall simulate the sound of a ship at sea."
JSON: {{"Action": ["takes", "simulate"]}}

Requirement: {{text}}
JSON:""",

    "System_response": f"""{SHARED_RULES}
Task: Extract the "System_response" (The specific behavior of the system).
Example: "When the offensive player takes a shot the product shall simulate the sound of a ship at sea."
JSON: {{"System_response": ["simulate the sound of a ship at sea"]}}

Requirement: {{text}}
JSON:"""
}