"""
Structured, typed outputs for every agent in the pipeline.

Every agent in agents/ sets `output_type=<one of these>` on its SDK Agent
definition, so the model is forced to return validated, machine-readable
data instead of free text. The orchestrator stores each of these on the
SharedContext as the run progresses.
"""
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class Task(BaseModel):
    id: str = Field(description="Short unique task id, e.g. 'T1'")
    description: str
    owner_agent: str = Field(
        description="Which downstream agent should perform this: "
        "research | domain_expert | execution"
    )
    success_criteria: str


class TaskPlan(BaseModel):
    goal: str
    business_context: str = Field(description="1-3 sentence restatement of the business context")
    stakeholders: List[str]
    objectives: List[str]
    tasks: List[Task]


class ResearchFinding(BaseModel):
    topic: str
    summary: str
    source: str
    confidence: float = Field(ge=0.0, le=1.0)


class ResearchFindings(BaseModel):
    findings: List[ResearchFinding]
    open_questions: List[str] = Field(default_factory=list)


class DomainAnalysis(BaseModel):
    analysis_summary: str
    key_metrics: dict = Field(
        default_factory=dict,
        description="Named quantitative metrics computed via data_analysis_tool, e.g. {'avg_cost': 120000}",
    )
    risks: List[str]
    opportunities: List[str]


class ScenarioResult(BaseModel):
    name: str
    projected_roi_pct: float
    payback_period_months: float
    notes: str


class ExecutionResult(BaseModel):
    actions_modelled: List[str]
    scenarios: List[ScenarioResult]
    recommended_scenario: str
    requires_human_approval: bool = True


class ReviewResult(BaseModel):
    approved: bool
    issues_found: List[str] = Field(default_factory=list)
    reviewer_notes: str


class ExecutiveReport(BaseModel):
    title: str
    executive_summary: str
    key_findings: List[str]
    recommendation: str
    financial_projection: Optional[ScenarioResult] = None
    risks: List[str]
    next_steps: List[str]
