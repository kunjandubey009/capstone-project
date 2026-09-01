# capstone-project
# AI Autonomous Business Operations Platform

A multi-agent enterprise system, built on the **OpenAI Agents SDK**, that takes a
high-level business goal, breaks it into executable tasks, delegates work to
specialised agents, coordinates execution through tool calls, reviews the
outcome, and produces an executive-ready recommendation — with a human
approval checkpoint before anything is finalised.

---

## 1. Problem Analysis

### Business Context
Enterprise teams are regularly handed vague, high-level directives —
*"reduce operating costs by 15% this quarter"*, *"evaluate whether we should
enter the Southeast Asia market"*, *"improve customer retention"* — that
require research, domain expertise, quantitative modelling, and a polished
write-up before anyone acts on them. Today that work is manual, spread across
several people/tools, and slow to turn around.

### Stakeholders
| Stakeholder | Interest |
|---|---|
| Executive sponsor (COO/CFO/CEO) | Wants a fast, trustworthy recommendation with clear numbers |
| Business unit owner | Needs the plan grounded in their operational reality |
| Analyst / Ops team | Currently does this work by hand; wants it accelerated, not replaced blindly |
| Compliance / Risk | Needs a human checkpoint before any action is executed or communicated externally |
| IT / Platform team | Needs the system to be auditable, extensible, and safe to run against internal tools |

### Problem Statement
Build a platform where autonomous, specialised AI agents collaborate — under
a human-in-the-loop approval gate — to take a business goal from ambiguous
statement to a reviewed, decision-ready executive report, while keeping a
shared record of what was found, decided, and why.

### Objectives
1. Accept a single natural-language business goal as input.
2. Autonomously decompose it into a concrete task plan.
3. Route tasks to the right domain-specialist agent(s).
4. Use tools (search, data analysis, financial modelling, knowledge base,
   notifications) to gather evidence and produce quantitative outputs.
5. Maintain shared memory/context so every agent works off the same facts.
6. Produce **structured, typed outputs** at every stage (not free-text blobs).
7. Insert a **human approval checkpoint** before execution actions and before
   the final report is distributed.
8. Emit a final executive report summarising findings, options, and a
   recommendation.

---

## 2. Multi-Agent Design

### Agent Architecture

```
                         ┌─────────────────┐
                         │   User Goal      │
                         └────────┬─────────┘
                                  ▼
                         ┌─────────────────┐
                         │  Planner Agent   │  <- decomposes goal into tasks
                         └────────┬─────────┘
                                  ▼ handoff
                         ┌─────────────────┐
                         │  Research Agent  │  <- web_search_tool, knowledge_base_tool
                         └────────┬─────────┘
                                  ▼ handoff
                         ┌───────────────────┐
                         │ Domain Expert Agent│ <- knowledge_base_tool, data_analysis_tool
                         └────────┬───────────┘
                                  ▼ handoff
                         ┌─────────────────┐
                         │ Execution Agent  │  <- data_analysis_tool, financial_calculator_tool
                         └────────┬─────────┘
                                  ▼ handoff
                    ┌──────────► HUMAN APPROVAL GATE ◄──────────┐
                    │             (before execution commits)     │
                    ▼                                            │
           ┌─────────────────┐                                   │
           │ Reviewer Agent  │  <- validates against plan/policy  │
           └────────┬────────┘                                   │
                     ▼ handoff                                    │
           ┌───────────────────┐                                  │
           │ Report Generator  │  <- notification_tool             │
           └────────┬───────────┘                                  │
                     ▼                                             │
              HUMAN APPROVAL GATE ─────────────────────────────────┘
              (before report is sent/published)
                     ▼
              Final Executive Report

     ══════════ Shared Memory / Context (Memory Manager) ══════════
     accessible to every agent throughout the run — goal, task plan,
     research findings, domain analysis, execution results, review notes
```

### Roles of Each Agent

| # | Agent | Responsibility | Output type |
|---|---|---|---|
| 1 | **Planner Agent** | Breaks the business goal into an ordered list of tasks with owners and success criteria | `TaskPlan` |
| 2 | **Research Agent** | Gathers external/market evidence via search + internal knowledge base | `ResearchFindings` |
| 3 | **Domain Expert Agent** | Applies domain-specific reasoning (finance/ops/market) to interpret research and run quantitative analysis | `DomainAnalysis` |
| 4 | **Execution Agent** | Turns analysis into concrete modelled actions (cost/ROI scenarios, resourcing) using tools; halts for human approval before "committing" | `ExecutionResult` |
| 5 | **Reviewer Agent** | Quality/policy/compliance check of everything produced so far against the original plan | `ReviewResult` |
| 6 | **Report Generator Agent** | Synthesises all prior structured outputs into an executive report and (after approval) dispatches a notification | `ExecutiveReport` |
| — | **Memory Manager** | Not an LLM agent — a shared context/state service every agent reads from and writes to, so nothing is re-derived or lost across handoffs | `SharedContext` |

### Agent Interaction & Handoff Flow
The orchestrator (`workflows/orchestrator.py`) runs agents **linearly with
explicit SDK `handoff`s**: Planner → Research → Domain Expert → Execution →
(human approval) → Reviewer → Report Generator → (human approval) → done.
Every agent:
- reads the `SharedContext` (via `RunContextWrapper`) instead of re-asking the
  user for information already gathered,
- returns a **typed Pydantic object** (`output_type=...`) rather than free text,
- writes its result back into `SharedContext` before handing off.

If the Reviewer Agent rejects a step, the orchestrator routes back to the
relevant upstream agent (Domain Expert or Execution) instead of proceeding —
a simple retry loop capped at 2 attempts.

### Tool Integration Overview

| Tool | Used by | Purpose |
|---|---|---|
| `web_search_tool` | Research Agent | External market/competitor/industry signal (stubbed adapter — swap in Bing/Tavily/Google in production) |
| `knowledge_base_tool` | Research, Domain Expert | Retrieval over internal company documents (stubbed in-memory vector-style lookup) |
| `data_analysis_tool` | Domain Expert, Execution | Runs pandas-based aggregation/statistics over supplied datasets |
| `financial_calculator_tool` | Execution Agent | ROI, NPV, payback period, cost-saving projections |
| `notification_tool` | Report Generator | Sends the final report out (stubbed Slack/email adapter) |

All tools are implemented as `@function_tool`-decorated Python functions with
typed arguments, so the SDK auto-generates their JSON schema for the model.
Every tool that is "stubbed" is isolated behind a small adapter function —
swapping in a real API only means editing that one function.

---

## 3. Implementation Notes

- **Minimum 5 specialised agents** → 6 implemented (`specialists/`).
- **Minimum 5 tools/APIs** → 5 implemented (`tools/`).
- **Agent handoffs** → `agents.handoff()` wiring in `workflows/orchestrator.py`.
- **Memory/context management** → `memory/shared_memory.py` (`SharedContext`,
  passed as the SDK's run `context` and mutated by every agent).
- **Structured outputs** → every agent has a Pydantic `output_type` in
  `models/schemas.py`.
- **Human approval** → `workflows/orchestrator.py::human_approval_gate()`,
  called before the Execution Agent commits and before the final report is
  released. In a CLI run this prompts on stdin; swap it for a Slack
  approval-button webhook or a web UI callback in production.

### Project layout
```
ai-business-ops-platform/
├── README.md
├── requirements.txt
├── .env.example
├── config.py
├── main.py                    # entry point (real, requires OPENAI_API_KEY)
├── demo_offline.py            # dependency-free simulation of the same flow
├── models/schemas.py          # Pydantic structured-output models
├── tools/                     # 5 function_tools
├── specialists/                # 6 specialised agents (named to avoid
│                                # shadowing the SDK's own `agents` package)
├── memory/shared_memory.py    # Memory Manager
├── workflows/orchestrator.py  # handoff flow + human approval gates
└── output/                    # generated reports land here
```

### Running it

```bash
pip install -r requirements.txt
cp .env.example .env      # add your OPENAI_API_KEY
python main.py "Evaluate whether we should open a distribution center in Texas"
```

This requires network access and an OpenAI API key (the OpenAI Agents SDK
calls the Responses API under the hood).

### Running the offline demo (no API key / no network needed)
`demo_offline.py` runs the exact same agent pipeline, tool set, memory
manager, structured-output models, handoff sequence, and human-approval gate
— but with each "agent" replaced by a deterministic rule-based stand-in
instead of an LLM call. Use it to see and test the end-to-end architecture
and data flow immediately:

```bash
python demo_offline.py "Evaluate whether we should open a distribution center in Texas"
```

### Extending it
- Swap any tool's internals (in `tools/`) for a real API — the `@function_tool`
  signature is the only contract the agents rely on.
- Add an agent by: defining its Pydantic output model, writing its
  `Agent(...)` definition with `instructions` + `tools` + `output_type`, and
  inserting it into the handoff chain in `orchestrator.py`.
- Replace the CLI `human_approval_gate()` with a webhook/UI callback for
  production use.
