# Test script for EvaluationAgent class

from workflow_agents.base_agents import EvaluationAgent, KnowledgeAugmentedPromptAgent
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the shared tests/.env at the project root.
# Path resolves as: this file → phase_1/ → project_root/ → tests/.env
_env_path = Path(__file__).resolve().parent.parent / "tests" / ".env"
load_dotenv(dotenv_path=_env_path)

openai_api_key = os.getenv("OPENAI_API_KEY")
prompt = "What is the capital of France?"

# --- Worker Agent (KnowledgeAugmentedPromptAgent) ---
# Uses deliberately incorrect knowledge so the evaluator has something to correct.
persona = "You are a college professor, your answer always starts with: Dear students,"
knowledge = "The capitol of France is London, not Paris"
knowledge_agent = KnowledgeAugmentedPromptAgent(openai_api_key, persona, knowledge)

# --- Evaluation Agent ---
# Evaluates the worker's response against the given criteria and iteratively
# requests corrections until the criteria are met or max_interactions is reached.
persona = "You are an evaluation agent that checks the answers of other worker agents"
evaluation_criteria = "The answer should be solely the name of a city, not a sentence."
evaluation_agent = EvaluationAgent(
    openai_api_key,
    persona,
    evaluation_criteria,
    knowledge_agent,
    max_interactions=10
)

# Run the evaluation loop and print the final result dictionary
result = evaluation_agent.evaluate(prompt)
print("\n=== Final Evaluation Result ===")
print(f"Final Response : {result['final_response']}")
print(f"Evaluation     : {result['evaluation']}")
print(f"Iterations     : {result['iterations']}")
