"""
demo_offline.py — runs the SAME architecture (agents, handoffs, shared memory,
structured outputs, tools, human approval gates) as main.py, but with each
LLM agent replaced by a deterministic rule-based stand-in. No OpenAI API key,
no network, and no `openai-agents` package required — only `pydantic`
(and `pandas`, already a project dependency).

Use this to inspect/test the data flow and human-approval UX before wiring
up real API keys.

Usage:
    python demo_offline.py "Evaluate whether we should open a distribution center in Texas"
"""
from __future__ import annotations
import sys
import json
import os

from models.schemas import (
    Task, TaskPlan, ResearchFinding, ResearchFindings, DomainAnalysis,
    ScenarioResult, ExecutionResult, ReviewResult, ExecutiveReport,
)
from memory.shared_memory import SharedContext

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ---- Stand-ins for the 5 tools (same shape as tools/*.py, no SDK needed) ----

def mock_web_search(query: str, max_results: int = 3) -> list[dict]:
    return [{"title": f"Industry report: {query}", "url": "https://example.com"} for _ in range(max_results)]


def mock_knowledge_base(query: str, top_k: int = 2) -> list[dict]:
    return [{"id": "doc-1", "title": "FY25 Operating Cost Breakdown"}][:top_k]


def mock_financial_calc(initial_investment: float, annual_cash_flows: list[float], discount_rate_pct: float = 8.0) -> dict:
    total = sum(annual_cash_flows)
    roi_pct = ((total - initial_investment) / initial_investment) * 100 if initial_investment else 0.0
    cumulative, payback_years = 0.0, None
    for i, cf in enumerate(annual_cash_flows, start=1):
        cumulative += cf
        if cumulative >= initial_investment and payback_years is None:
            prior = cumulative - cf
            payback_years = (i - 1) + ((initial_investment - prior) / cf if cf else 0)
    r = discount_rate_pct / 100.0
    npv = -initial_investment + sum(cf / ((1 + r) ** yr) for yr, cf in enumerate(annual_cash_flows, start=1))
    return {
        "roi_pct": round(roi_pct, 2),
        "payback_period_months": round(payback_years * 12, 1) if payback_years else None,
        "npv": round(npv, 2),
    }


# ---- Stand-ins for the 6 agents ----

def planner_agent(goal: str) -> TaskPlan:
    return TaskPlan(
        goal=goal,
        business_context=f"The organisation needs a decision-ready recommendation on: {goal}",
        stakeholders=["Executive Sponsor", "Business Unit Owner", "Compliance", "Ops Team"],
        objectives=["Understand the opportunity", "Quantify the financial case", "Produce a clear recommendation"],
        tasks=[
            Task(id="T1", description="Gather market and internal evidence", owner_agent="research", success_criteria="At least 2 findings with sources"),
            Task(id="T2", description="Analyse findings and quantify risk/opportunity", owner_agent="domain_expert", success_criteria="Key metrics computed"),
            Task(id="T3", description="Model financial scenarios", owner_agent="execution", success_criteria="ROI and payback computed for >=2 scenarios"),
        ],
    )


def research_agent(ctx: SharedContext) -> ResearchFindings:
    mock_web_search(ctx.goal)
    mock_knowledge_base(ctx.goal)
    return ResearchFindings(
        findings=[
            ResearchFinding(topic="Market signal", summary=f"Simulated public-web signal relevant to '{ctx.goal}'.", source="https://example.com", confidence=0.6),
            ResearchFinding(topic="Internal cost baseline", summary="Logistics/warehousing is ~34% of regional operating cost (FY25 doc).", source="FY25 Operating Cost Breakdown", confidence=0.9),
        ],
        open_questions=["What is the target launch timeline?"],
    )


def domain_expert_agent(ctx: SharedContext) -> DomainAnalysis:
    return DomainAnalysis(
        analysis_summary="Evidence suggests the initiative is viable if paired with a local partner in year one, per past market-entry patterns.",
        key_metrics={"baseline_operating_cost_share_pct": 34.0},
        risks=["Requires legal/compliance sign-off before any public announcement", "Assumes stable demand"],
        opportunities=["Faster time-to-market via a local distribution partner"],
    )


def execution_agent(ctx: SharedContext) -> ExecutionResult:
    conservative = mock_financial_calc(500_000, [150_000, 180_000, 200_000])
    aggressive = mock_financial_calc(900_000, [250_000, 350_000, 420_000])
    scenarios = [
        ScenarioResult(name="Conservative rollout", projected_roi_pct=conservative["roi_pct"], payback_period_months=conservative["payback_period_months"] or 0, notes="Lower upfront spend, slower ramp."),
        ScenarioResult(name="Aggressive rollout", projected_roi_pct=aggressive["roi_pct"], payback_period_months=aggressive["payback_period_months"] or 0, notes="Higher upfront spend, faster ramp, higher risk."),
    ]
    best = max(scenarios, key=lambda s: s.projected_roi_pct)
    return ExecutionResult(
        actions_modelled=["Model conservative rollout", "Model aggressive rollout"],
        scenarios=scenarios,
        recommended_scenario=best.name,
        requires_human_approval=True,
    )


def reviewer_agent(ctx: SharedContext) -> ReviewResult:
    issues = []
    if not ctx.research or len(ctx.research.findings) < 1:
        issues.append("Insufficient research findings")
    if not ctx.execution_result or not ctx.execution_result.scenarios:
        issues.append("No scenarios modelled")
    return ReviewResult(approved=len(issues) == 0, issues_found=issues, reviewer_notes="Automated consistency check passed." if not issues else "Issues found; see issues_found.")


def report_generator_agent(ctx: SharedContext) -> ExecutiveReport:
    best_scenario = next(s for s in ctx.execution_result.scenarios if s.name == ctx.execution_result.recommended_scenario)
    return ExecutiveReport(
        title=f"Executive Recommendation: {ctx.goal}",
        executive_summary=(
            f"Based on research and financial modelling, we recommend proceeding with the "
            f"'{best_scenario.name}' scenario, projecting {best_scenario.projected_roi_pct}% ROI "
            f"with a payback period of {best_scenario.payback_period_months} months."
        ),
        key_findings=[f.summary for f in ctx.research.findings],
        recommendation=f"Proceed with: {best_scenario.name}",
        financial_projection=best_scenario,
        risks=ctx.domain_analysis.risks,
        next_steps=["Secure compliance sign-off", "Finalise budget", "Kick off implementation"],
    )


def human_approval_gate(ctx: SharedContext, gate_name: str, summary: str) -> bool:
    print("\n" + "=" * 70)
    print(f"HUMAN APPROVAL REQUIRED: {gate_name}")
    print("=" * 70)
    print(summary)
    answer = input("\nApprove? [y/N]: ").strip().lower()
    approved = answer == "y"
    ctx.record_approval(gate_name, approved)
    return approved


def run_pipeline(goal: str) -> SharedContext:
    ctx = SharedContext(goal=goal)
    ctx.log("orchestrator", "run_started", goal)

    ctx.task_plan = planner_agent(goal)
    ctx.log("planner_agent", "task_plan_created", f"{len(ctx.task_plan.tasks)} tasks")

    ctx.research = research_agent(ctx)
    ctx.log("research_agent", "research_completed", f"{len(ctx.research.findings)} findings")

    ctx.domain_analysis = domain_expert_agent(ctx)
    ctx.log("domain_expert_agent", "analysis_completed")

    ctx.execution_result = execution_agent(ctx)
    ctx.log("execution_agent", "execution_modelled", f"recommended: {ctx.execution_result.recommended_scenario}")

    if not human_approval_gate(
        ctx, "execution_scenarios",
        f"Execution Agent recommends: '{ctx.execution_result.recommended_scenario}'\n"
        f"Scenarios modelled: {[s.name for s in ctx.execution_result.scenarios]}",
    ):
        ctx.log("orchestrator", "run_halted", "execution scenarios not approved")
        return ctx

    ctx.review = reviewer_agent(ctx)
    ctx.log("reviewer_agent", "review_completed", f"approved={ctx.review.approved}")
    if not ctx.review.approved:
        ctx.log("orchestrator", "run_halted", "reviewer did not approve")
        return ctx

    ctx.report = report_generator_agent(ctx)
    ctx.log("report_generator_agent", "report_drafted", ctx.report.title)

    if human_approval_gate(
        ctx, "final_report_dispatch",
        f"Title: {ctx.report.title}\n\nSummary: {ctx.report.executive_summary}\n\n"
        f"Recommendation: {ctx.report.recommendation}",
    ):
        ctx.log("orchestrator", "report_dispatched", "channel=slack (mocked)")
    else:
        ctx.log("orchestrator", "report_dispatch_declined")

    return ctx


def main():
    goal = " ".join(sys.argv[1:]) or input("Enter a business goal: ")
    ctx = run_pipeline(goal)

    out_path = os.path.join(OUTPUT_DIR, "run_snapshot_offline.json")
    with open(out_path, "w") as f:
        json.dump(ctx.snapshot(), f, indent=2, default=str)

    print(f"\nRun complete. Snapshot written to {out_path}")
    if ctx.report:
        print("\n--- EXECUTIVE REPORT ---")
        print(f"Title: {ctx.report.title}")
        print(f"\n{ctx.report.executive_summary}")
        print(f"\nRecommendation: {ctx.report.recommendation}")


if __name__ == "__main__":
    main()
