# Test script for DirectPromptAgent class

from workflow_agents.base_agents import DirectPromptAgent
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the shared tests/.env at the project root.
# Path resolves as: this file → phase_1/ → project_root/ → tests/.env
_env_path = Path(__file__).resolve().parent.parent / "tests" / ".env"
load_dotenv(dotenv_path=_env_path)

# Load the OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

prompt = "What is the Capital of France?"

# Instantiate the DirectPromptAgent
direct_agent = DirectPromptAgent(openai_api_key)

# Send the prompt and store the response
direct_agent_response = direct_agent.respond(prompt)

# Print the response from the agent
print(f"Prompt: {prompt}")
print(f"Response: {direct_agent_response}")

# The agent relies entirely on the LLM's pre-trained knowledge (no system prompt,
# no additional context, no memory). It is the simplest possible agent pattern —
# the user message goes straight to GPT-3.5-turbo and the raw text comes back.
print(
    "\nKnowledge source: The DirectPromptAgent uses only the general knowledge "
    "embedded in the GPT-3.5-turbo model during its training. No system prompt, "
    "retrieval, or external context is provided — the answer comes entirely from "
    "the model's pre-trained world knowledge."
)
