"""Agent 6/6: Report Generator Agent — synthesises everything into an executive report."""
from agents import Agent
import config
from models.schemas import ExecutiveReport

report_generator_agent = Agent(
    name="Report Generator Agent",
    model=config.DEFAULT_MODEL,
    instructions=(
        "You are the Report Generator Agent. You receive the full approved "
        "run: TaskPlan, ResearchFindings, DomainAnalysis, ExecutionResult, "
        "and ReviewResult. Synthesise all of it into a single ExecutiveReport: "
        "a punchy title, a 3-5 sentence executive_summary, a bullet list of "
        "key_findings, a single clear recommendation, the recommended "
        "financial_projection (pulled from the Execution Agent's recommended "
        "scenario), a list of risks, and concrete next_steps. Write for a "
        "time-pressed executive — no filler. You only draft the report; "
        "dispatch happens separately after a human approves it."
    ),
    output_type=ExecutiveReport,
)
