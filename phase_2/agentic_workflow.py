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

# TODO 2 – Load the OpenAI API key from the .env file
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
# Explicitly lists the three sequential project-management steps so the agent
# always returns exactly three ordered steps regardless of the prompt wording.
knowledge_action_planning = (
    "A development plan for a product contains three sequential steps:\n"
    "Step 1: Define user stories from the product specification by identifying personas, "
    "actions, and desired outcomes. Each story follows the format: As a [type of user], "
    "I want [an action or feature] so that [benefit/value].\n"
    "Step 2: Define product features by grouping related user stories into cohesive capabilities.\n"
    "Step 3: Define engineering tasks for each user story, specifying the technical work required.\n"
    "When asked to create a development plan, return these three steps in order."
)

# TODO 4 – Instantiate the ActionPlanningAgent
action_planning_agent = ActionPlanningAgent(openai_api_key, knowledge_action_planning)

# ── Product Manager ────────────────────────────────────────────────────────────

persona_product_manager = (
    "You are a Product Manager, you are responsible for defining the user stories for a product."
)
# TODO 5 – Complete knowledge string by appending the product_spec
knowledge_product_manager = (
    "Stories are defined by writing sentences with a persona, an action, and a desired outcome. "
    "The sentences always start with: As a "
    "Write several stories for the product spec below, where the personas are the different "
    "users of the product. "
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
# Includes product spec so features reference the Email Router's actual capabilities
knowledge_program_manager = (
    "Features of a product are defined by organizing similar user stories into cohesive groups. "
    "Each feature must have a Feature Name, Description, Key Functionality, and User Benefit. "
    "Base your features on this product specification:\n"
    + product_spec
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
# Includes product spec so tasks reference Email Router components specifically
knowledge_dev_engineer = (
    "Development tasks are defined by identifying what needs to be built to implement each user story. "
    "Each task must include Task ID, Task Title, Related User Story, Description, "
    "Acceptance Criteria, Estimated Effort, and Dependencies. "
    "Base your tasks on this product specification:\n"
    + product_spec
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

# ── Workflow Context Accumulator ───────────────────────────────────────────────
# Stores outputs from each step so downstream agents can reference prior work.
# Program Manager receives the user stories; Dev Engineer receives both stories
# and features, ensuring all output is grounded in the Email Router spec.

workflow_context = {
    "user_stories": "",
    "product_features": "",
}

# ── Support Functions (TODO 11) ────────────────────────────────────────────────

def product_manager_support_function(query):
    """
    Generate and evaluate user stories for the Email Router.
    Stores results in workflow_context for use by downstream agents.
    """
    initial_response = product_manager_knowledge_agent.respond(query)
    evaluation_result = product_manager_evaluation_agent.evaluate(initial_response)
    result = evaluation_result["final_response"]
    workflow_context["user_stories"] = result
    return result


def program_manager_support_function(query):
    """
    Generate and evaluate product features.
    Enriches the query with previously generated user stories so features
    are grounded in the actual stories produced for the Email Router.
    """
    enriched_query = query
    if workflow_context["user_stories"]:
        enriched_query = (
            f"{query}\n\n"
            f"Use these user stories as the basis for defining features:\n"
            f"{workflow_context['user_stories']}"
        )
    initial_response = program_manager_knowledge_agent.respond(enriched_query)
    evaluation_result = program_manager_evaluation_agent.evaluate(initial_response)
    result = evaluation_result["final_response"]
    workflow_context["product_features"] = result
    return result


def development_engineer_support_function(query):
    """
    Generate and evaluate engineering tasks.
    Enriches the query with user stories and features so tasks directly
    reference the Email Router stories and capabilities defined earlier.

    NOTE: We pass enriched_query directly to evaluate() instead of pre-calling
    respond() and passing that result. EvaluationAgent.evaluate() re-calls the
    worker agent with whatever argument it receives as the "prompt". If we pass
    the initial_response (ET1-ET9) instead of the original query, the worker
    treats the existing tasks as a prompt and only generates *additional* tasks
    (ET10-ET12), so final_response misses ET1-ET9. Passing the enriched_query
    lets the worker generate the complete task list in one shot.
    """
    context_parts = []
    if workflow_context["user_stories"]:
        context_parts.append(
            f"User stories for the Email Router:\n{workflow_context['user_stories']}"
        )
    if workflow_context["product_features"]:
        context_parts.append(
            f"Product features for the Email Router:\n{workflow_context['product_features']}"
        )

    enriched_query = (
        f"{query}\n\n" + "\n\n".join(context_parts)
        if context_parts else query
    )
    # Pass enriched_query directly so the worker generates all tasks in one shot
    # and final_response captures the complete engineering task breakdown.
    evaluation_result = development_engineer_evaluation_agent.evaluate(enriched_query)
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

# Comprehensive prompt that explicitly requests all three project-plan components
workflow_prompt = (
    "Create a comprehensive development plan for the Email Router product. "
    "This plan should include: "
    "1. User stories that define the personas and their needs, "
    "2. Product features that group related functionality, "
    "3. Detailed engineering tasks for implementation."
)
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

# ── Final Output: print all three sections of the project plan ─────────────────
print("\n" + "="*60)
print("*** FINAL WORKFLOW OUTPUT — EMAIL ROUTER PROJECT PLAN ***")
print("="*60)

section_labels = ["USER STORIES", "PRODUCT FEATURES", "ENGINEERING TASKS"]
for idx, result in enumerate(completed_steps):
    label = section_labels[idx] if idx < len(section_labels) else f"STEP {idx + 1}"
    print(f"\n{'─'*60}")
    print(f"  {label}")
    print(f"{'─'*60}")
    print(result)

print("\n" + "="*60)
print("*** END OF EMAIL ROUTER PROJECT PLAN ***")
print("="*60)
