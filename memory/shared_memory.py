"""
Memory Manager.

Rather than an LLM agent, the Memory Manager is a lightweight, typed context
object shared across every step of the run. This is the SDK's recommended
pattern: pass a `context` object into `Runner.run(..., context=shared_ctx)`
and every `@function_tool` / agent hook receives it via `RunContextWrapper`.

Keeping this as plain Python (not an LLM call) means:
  - zero risk of the "memory" being hallucinated or dropped,
  - it's cheap and instant to read/write,
  - it doubles as the audit trail for the whole run (see `.history`).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, List, Optional

from models.schemas import (
    TaskPlan,
    ResearchFindings,
    DomainAnalysis,
    ExecutionResult,
    ReviewResult,
    ExecutiveReport,
)


@dataclass
class HistoryEntry:
    timestamp: str
    agent: str
    event: str
    detail: str = ""


@dataclass
class SharedContext:
    """The single source of truth passed between every agent in the run."""

    goal: str
    task_plan: Optional[TaskPlan] = None
    research: Optional[ResearchFindings] = None
    domain_analysis: Optional[DomainAnalysis] = None
    execution_result: Optional[ExecutionResult] = None
    review: Optional[ReviewResult] = None
    report: Optional[ExecutiveReport] = None
    approvals: dict = field(default_factory=dict)  # gate_name -> bool
    history: List[HistoryEntry] = field(default_factory=list)

    def log(self, agent: str, event: str, detail: str = "") -> None:
        self.history.append(
            HistoryEntry(
                timestamp=datetime.now(timezone.utc).isoformat(),
                agent=agent,
                event=event,
                detail=detail,
            )
        )

    def record_approval(self, gate_name: str, approved: bool) -> None:
        self.approvals[gate_name] = approved
        self.log("human", "approval_gate", f"{gate_name} -> {approved}")

    def snapshot(self) -> dict:
        """A serialisable snapshot, useful for logging/report generation."""
        return {
            "goal": self.goal,
            "task_plan": self.task_plan.model_dump() if self.task_plan else None,
            "research": self.research.model_dump() if self.research else None,
            "domain_analysis": self.domain_analysis.model_dump() if self.domain_analysis else None,
            "execution_result": self.execution_result.model_dump() if self.execution_result else None,
            "review": self.review.model_dump() if self.review else None,
            "report": self.report.model_dump() if self.report else None,
            "approvals": self.approvals,
            "history": [h.__dict__ for h in self.history],
        }
