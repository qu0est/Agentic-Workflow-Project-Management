# Test script for KnowledgeAugmentedPromptAgent class

from workflow_agents.base_agents import KnowledgeAugmentedPromptAgent
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the shared tests/.env at the project root.
# Path resolves as: this file → phase_1/ → project_root/ → tests/.env
_env_path = Path(__file__).resolve().parent.parent / "tests" / ".env"
load_dotenv(dotenv_path=_env_path)

# Load the OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")

prompt = "What is the capital of France?"

persona = "You are a college professor, your answer always starts with: Dear students,"

# Instantiate a KnowledgeAugmentedPromptAgent with:
#   - Persona: college professor
#   - Knowledge: deliberately incorrect fact to prove the agent uses provided knowledge
knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key,
    persona,
    "The capital of France is London, not Paris"
)

response = knowledge_agent.respond(prompt)
print(f"Prompt: {prompt}")
print(f"Response:\n{response}")

# Confirming that the agent uses the provided knowledge rather than its inherent LLM knowledge:
# GPT-3.5-turbo knows the correct answer is Paris. However, because the agent's system
# prompt explicitly supplies "The capital of France is London, not Paris" as the ONLY
# allowed knowledge source, the model should respond with London — demonstrating that
# provided knowledge overrides the model's training data.
print(
    "\nVerification: The response above should state 'London' as the capital of France. "
    "This confirms the KnowledgeAugmentedPromptAgent uses the provided knowledge "
    "('The capital of France is London, not Paris') rather than its inherent LLM knowledge (Paris)."
)
