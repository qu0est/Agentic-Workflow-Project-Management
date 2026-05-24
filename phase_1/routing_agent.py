# Test script for RoutingAgent class

from workflow_agents.base_agents import KnowledgeAugmentedPromptAgent, RoutingAgent
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the shared tests/.env at the project root.
# Path resolves as: this file → phase_1/ → project_root/ → tests/.env
_env_path = Path(__file__).resolve().parent.parent / "tests" / ".env"
load_dotenv(dotenv_path=_env_path)

openai_api_key = os.getenv("OPENAI_API_KEY")

persona = "You are a college professor"

# --- Texas Agent ---
knowledge = "You know everything about Texas"
texas_agent = KnowledgeAugmentedPromptAgent(openai_api_key, persona, knowledge)

# --- Europe Agent ---
knowledge = "You know everything about Europe"
europe_agent = KnowledgeAugmentedPromptAgent(openai_api_key, persona, knowledge)

# --- Math Agent ---
persona = "You are a college math professor"
knowledge = (
    "You know everything about math, you take prompts with numbers, "
    "extract math formulas, and show the answer without explanation"
)
math_agent = KnowledgeAugmentedPromptAgent(openai_api_key, persona, knowledge)

# Instantiate the RoutingAgent (agents list assigned below)
routing_agent = RoutingAgent(openai_api_key, {})

# Define the routes: each entry maps a description to the correct agent's respond method
agents = [
    {
        "name": "texas agent",
        "description": "Answer a question about Texas",
        "func": lambda x: texas_agent.respond(x)
    },
    {
        "name": "europe agent",
        "description": "Answer a question about Europe",
        "func": lambda x: europe_agent.respond(x)
    },
    {
        "name": "math agent",
        "description": "When a prompt contains numbers, respond with a math formula",
        "func": lambda x: math_agent.respond(x)
    }
]

routing_agent.agents = agents

# Test 1 – should route to the Texas agent
prompt1 = "Tell me about the history of Rome, Texas"
print(f"\nPrompt: {prompt1}")
print(f"Response:\n{routing_agent.route(prompt1)}")

# Test 2 – should route to the Europe agent
prompt2 = "Tell me about the history of Rome, Italy"
print(f"\nPrompt: {prompt2}")
print(f"Response:\n{routing_agent.route(prompt2)}")

# Test 3 – should route to the math agent
prompt3 = "One story takes 2 days, and there are 20 stories"
print(f"\nPrompt: {prompt3}")
print(f"Response:\n{routing_agent.route(prompt3)}")
