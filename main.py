"""
Entry point for the real, LLM-powered pipeline.

Usage:
    python main.py "Evaluate whether we should open a distribution center in Texas"

Requires: `pip install -r requirements.txt`, network access, and a valid
OPENAI_API_KEY in your environment / .env file.
"""
import sys
import json
import os

import config
from workflows.orchestrator import run_pipeline


def main():
    if not config.OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY is not set. Copy .env.example to .env and add your key.")
        sys.exit(1)

    goal = " ".join(sys.argv[1:]) or input("Enter a business goal: ")

    ctx = run_pipeline(goal)

    out_path = os.path.join(config.OUTPUT_DIR, "run_snapshot.json")
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
