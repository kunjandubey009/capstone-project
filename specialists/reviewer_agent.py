"""Agent 5/6: Reviewer Agent — quality/policy check before the report is written."""
from agents import Agent
import config
from models.schemas import ReviewResult
from tools.knowledge_base_tool import knowledge_base_tool

reviewer_agent = Agent(
    name="Reviewer Agent",
    model=config.DEFAULT_MODEL,
    instructions=(
        "You are the Reviewer Agent, the quality and compliance gate. You "
        "receive the full run so far: TaskPlan, ResearchFindings, "
        "DomainAnalysis, and ExecutionResult. Check for: (1) internal "
        "consistency — do the numbers and claims agree with each other, "
        "(2) whether every objective in the TaskPlan was actually addressed, "
        "(3) compliance concerns — use knowledge_base_tool to check company "
        "policy documents (e.g. anything requiring legal/compliance sign-off). "
        "Return a ReviewResult: set approved to false if there are material "
        "gaps, unsupported numbers, or unresolved compliance flags, and list "
        "every issue_found. Otherwise set approved to true. Always include "
        "clear reviewer_notes explaining the decision."
    ),
    tools=[knowledge_base_tool],
    output_type=ReviewResult,
)
