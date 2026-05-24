"""
agentic_workflow.py

General-purpose agentic workflow for technical project management.
Pilot: Email Router product specification.

Orchestrates ActionPlanningAgent, KnowledgeAugmentedPromptAgent,
EvaluationAgent, and RoutingAgent to produce user stories, product
features, and engineering tasks from a product spec document.
"""

# TODO 1 – Import required agents from the workflow_agents package
from workflow_agents.base_agents import (
    ActionPlanningAgent,
    KnowledgeAugmentedPromptAgent,
    EvaluationAgent,
    RoutingAgent,
)

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the shared tests/.env at the project root.
# Path resolves as: this file → phase_2/ → project_root/ → tests/.env
_env_path = Path(__file__).resolve().parent.parent / "tests" / ".env"
load_dotenv(dotenv_path=_env_path)
openai_api_key = os.getenv("OPENAI_API_KEY")

# TODO 3 – Load the Email Router product specification into a string
spec_path = os.path.join(os.path.dirname(__file__), "workflow_agents", "Product-Spec-Email-Router.txt")
with open(spec_path, "r", encoding="utf-8") as f:
    product_spec = f.read()

# ── Agent Instantiation ────────────────────────────────────────────────────────

# Action Planning Agent
# Knows the three project-management artefacts (stories, features, tasks) and
# uses that knowledge to decompose any workflow prompt into concrete steps.
knowledge_action_planning = (
    "Stories are defined from a product spec by identifying a "
    "persona, an action, and a desired outcome for each story. "
    "Each story represents a specific functionality of the product "
    "described in the specification. \n"
    "Features are defined by grouping related user stories. \n"
    "Tasks are defined for each story and represent the engineering "
    "work required to develop the product. \n"
    "A development Plan for a product contains all these components"
)

# TODO 4 – Instantiate the ActionPlanningAgent
action_planning_agent = ActionPlanningAgent(openai_api_key, knowledge_action_planning)

# ── Product Manager ────────────────────────────────────────────────────────────

persona_product_manager = (
    "You are a Product Manager, you are responsible for defining the user stories for a product."
)
knowledge_product_manager = (
    "Stories are defined by writing sentences with a persona, an action, and a desired outcome. "
    "The sentences always start with: As a "
    "Write several stories for the product spec below, where the personas are the different users of the product. "
    # TODO 5 – Append the product spec so the agent has full context
    + product_spec
)

# TODO 6 – Instantiate the KnowledgeAugmentedPromptAgent for the Product Manager
product_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key,
    persona_product_manager,
    knowledge_product_manager,
)

# TODO 7 – Instantiate the EvaluationAgent for the Product Manager
persona_pm_eval = "You are an evaluation agent that checks the answers of other worker agents"
evaluation_criteria_pm = (
    "The answer should be stories that follow the following structure: "
    "As a [type of user], I want [an action or feature] so that [benefit/value]."
)
product_manager_evaluation_agent = EvaluationAgent(
    openai_api_key,
    persona_pm_eval,
    evaluation_criteria_pm,
    agent_to_evaluate=product_manager_knowledge_agent,
    max_interactions=3,
)

# ── Program Manager ────────────────────────────────────────────────────────────

persona_program_manager = (
    "You are a Program Manager, you are responsible for defining the features for a product."
)
knowledge_program_manager = (
    "Features of a product are defined by organizing similar user stories into cohesive groups."
)

# Instantiate the KnowledgeAugmentedPromptAgent for the Program Manager
program_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key,
    persona_program_manager,
    knowledge_program_manager,
)

# TODO 8 – Instantiate the EvaluationAgent for the Program Manager
persona_program_manager_eval = "You are an evaluation agent that checks the answers of other worker agents."
evaluation_criteria_pgm = (
    "The answer should be product features that follow the following structure: "
    "Feature Name: A clear, concise title that identifies the capability\n"
    "Description: A brief explanation of what the feature does and its purpose\n"
    "Key Functionality: The specific capabilities or actions the feature provides\n"
    "User Benefit: How this feature creates value for the user"
)
program_manager_evaluation_agent = EvaluationAgent(
    openai_api_key,
    persona_program_manager_eval,
    evaluation_criteria_pgm,
    agent_to_evaluate=program_manager_knowledge_agent,
    max_interactions=3,
)

# ── Development Engineer ───────────────────────────────────────────────────────

persona_dev_engineer = (
    "You are a Development Engineer, you are responsible for defining the development tasks for a product."
)
knowledge_dev_engineer = (
    "Development tasks are defined by identifying what needs to be built to implement each user story."
)

# Instantiate the KnowledgeAugmentedPromptAgent for the Development Engineer
development_engineer_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key,
    persona_dev_engineer,
    knowledge_dev_engineer,
)

# TODO 9 – Instantiate the EvaluationAgent for the Development Engineer
persona_dev_engineer_eval = "You are an evaluation agent that checks the answers of other worker agents."
evaluation_criteria_dev = (
    "The answer should be tasks following this exact structure: "
    "Task ID: A unique identifier for tracking purposes\n"
    "Task Title: Brief description of the specific development work\n"
    "Related User Story: Reference to the parent user story\n"
    "Description: Detailed explanation of the technical work required\n"
    "Acceptance Criteria: Specific requirements that must be met for completion\n"
    "Estimated Effort: Time or complexity estimation\n"
    "Dependencies: Any tasks that must be completed first"
)
development_engineer_evaluation_agent = EvaluationAgent(
    openai_api_key,
    persona_dev_engineer_eval,
    evaluation_criteria_dev,
    agent_to_evaluate=development_engineer_knowledge_agent,
    max_interactions=3,
)

# ── Support Functions (TODO 11) ────────────────────────────────────────────────
# Each function accepts a step string from the action plan, calls the
# corresponding knowledge agent, passes the result to the evaluation agent,
# and returns the final validated response.

def product_manager_support_function(query):
    """Generate and evaluate user stories for the given query."""
    initial_response = product_manager_knowledge_agent.respond(query)
    evaluation_result = product_manager_evaluation_agent.evaluate(initial_response)
    return evaluation_result["final_response"]


def program_manager_support_function(query):
    """Generate and evaluate product features for the given query."""
    initial_response = program_manager_knowledge_agent.respond(query)
    evaluation_result = program_manager_evaluation_agent.evaluate(initial_response)
    return evaluation_result["final_response"]


def development_engineer_support_function(query):
    """Generate and evaluate engineering tasks for the given query."""
    initial_response = development_engineer_knowledge_agent.respond(query)
    evaluation_result = development_engineer_evaluation_agent.evaluate(initial_response)
    return evaluation_result["final_response"]


# ── Routing Agent (TODO 10) ────────────────────────────────────────────────────

routing_agent = RoutingAgent(openai_api_key, [])
routing_agent.agents = [
    {
        "name": "Product Manager",
        "description": (
            "Responsible for defining product personas and user stories only. "
            "Does not define features or tasks. Does not group stories."
        ),
        "func": lambda x: product_manager_support_function(x),
    },
    {
        "name": "Program Manager",
        "description": (
            "Responsible for defining product features by grouping related user stories. "
            "Does not write user stories or engineering tasks."
        ),
        "func": lambda x: program_manager_support_function(x),
    },
    {
        "name": "Development Engineer",
        "description": (
            "Responsible for defining detailed engineering tasks and implementation work "
            "required to build each user story. Does not write stories or features."
        ),
        "func": lambda x: development_engineer_support_function(x),
    },
]

# ── Workflow Execution (TODO 12) ───────────────────────────────────────────────

print("\n*** Workflow execution started ***\n")

# The workflow prompt — a TPM's high-level request that drives the entire pipeline
workflow_prompt = "What would the development tasks for this product be?"
print(f"Task to complete in this workflow, workflow prompt = {workflow_prompt}")

print("\nDefining workflow steps from the workflow prompt")
workflow_steps = action_planning_agent.extract_steps_from_prompt(workflow_prompt)
print(f"\nWorkflow steps identified: {len(workflow_steps)}")
for idx, step in enumerate(workflow_steps, 1):
    print(f"  {idx}. {step}")

completed_steps = []

for step in workflow_steps:
    print(f"\n{'='*60}")
    print(f"Executing step: {step}")
    print("="*60)
    result = routing_agent.route(step)
    completed_steps.append(result)
    print(f"\nStep result:\n{result}")

print("\n" + "="*60)
print("*** FINAL WORKFLOW OUTPUT ***")
print("="*60)
if completed_steps:
    print(completed_steps[-1])
