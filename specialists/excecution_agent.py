"""Agent 4/6: Execution Agent — models concrete scenarios/actions with real math."""
from agents import Agent
import config
from models.schemas import ExecutionResult
from tools.data_analysis_tool import data_analysis_tool
from tools.financial_calculator_tool import financial_calculator_tool

execution_agent = Agent(
    name="Execution Agent",
    model=config.DEFAULT_MODEL,
    instructions=(
        "You are the Execution Agent. Using the TaskPlan and DomainAnalysis, "
        "model 2-3 concrete scenarios for how to pursue the business goal. "
        "Use financial_calculator_tool to compute real roi_pct, "
        "payback_period_months, and NPV for each scenario from reasonable "
        "cash-flow assumptions (state your assumptions in the scenario notes). "
        "Use data_analysis_tool if further numeric summarisation is useful. "
        "Return an ExecutionResult listing the actions_modelled, the "
        "scenarios (each a name, projected_roi_pct, payback_period_months, "
        "and notes), your recommended_scenario by name, and always set "
        "requires_human_approval to true — this agent never commits an action "
        "on its own, it only proposes and models it for a human to approve."
    ),
    tools=[data_analysis_tool, financial_calculator_tool],
    output_type=ExecutionResult,
)
