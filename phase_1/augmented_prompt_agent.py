# Test script for AugmentedPromptAgent class

from workflow_agents.base_agents import AugmentedPromptAgent
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the shared tests/.env at the project root.
# Path resolves as: this file → phase_1/ → project_root/ → tests/.env
_env_path = Path(__file__).resolve().parent.parent / "tests" / ".env"
load_dotenv(dotenv_path=_env_path)

# Retrieve OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

prompt = "What is the capital of France?"
persona = "You are a college professor; your answers always start with: 'Dear students,'"

# Instantiate an AugmentedPromptAgent with the required parameters
augmented_agent = AugmentedPromptAgent(openai_api_key, persona)

# Send the prompt to the agent and store the response
augmented_agent_response = augmented_agent.respond(prompt)

# Print the agent's response
print(f"Prompt: {prompt}")
print(f"Persona: {persona}")
print(f"Response:\n{augmented_agent_response}")

# Knowledge source: The AugmentedPromptAgent still draws its factual knowledge from
# GPT-3.5-turbo's pre-trained world knowledge — the same knowledge base as the
# DirectPromptAgent. No external data or retrieval is used.
#
# Impact of persona: Specifying the persona changes the STYLE and VOICE of the
# response, not the underlying facts. The model will frame its answer as a professor
# addressing students (prefixing with "Dear students,") and may adopt a more formal,
# educational tone. The persona is injected as a system prompt, which the model
# treats as authoritative framing for the entire conversation.
