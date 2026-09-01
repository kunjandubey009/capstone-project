"""Agent 1/6: Planner Agent — decomposes the business goal into a task plan."""
from agents import Agent
import config
from models.schemas import TaskPlan

planner_agent = Agent(
    name="Planner Agent",
    model=config.DEFAULT_MODEL,
    instructions=(
        "You are the Planner Agent for an enterprise operations platform. "
        "Given a single high-level business goal, produce a TaskPlan: restate "
        "the business context in 1-3 sentences, list the likely stakeholders, "
        "list clear objectives, and break the goal into 3-6 concrete tasks. "
        "Each task must have a short id (T1, T2, ...), a one-sentence "
        "description, an owner_agent chosen from exactly "
        "['research', 'domain_expert', 'execution'], and a measurable "
        "success_criteria. Order tasks so research happens before domain "
        "analysis, which happens before execution modelling. Do not solve "
        "the tasks yourself — only plan them."
    ),
    output_type=TaskPlan,
)
