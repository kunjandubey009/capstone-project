"""
Tool 3/5: data_analysis_tool

Runs simple, real aggregation/statistics over tabular data with pandas so
agents get grounded numbers instead of guessing them. Accepts data as a
list of flat dict rows (JSON-friendly for the tool-call interface).
"""
from agents import function_tool
import pandas as pd


@function_tool
def data_analysis_tool(rows: list[dict], numeric_column: str, group_by: str | None = None) -> dict:
    """Compute summary statistics over tabular data.

    Args:
        rows: List of records, each a flat dict of column -> value.
        numeric_column: Which numeric column to summarise.
        group_by: Optional column to group the summary by.
    """
    if not rows:
        return {"error": "no rows supplied"}

    df = pd.DataFrame(rows)
    if numeric_column not in df.columns:
        return {"error": f"column '{numeric_column}' not found", "columns": list(df.columns)}

    if group_by and group_by in df.columns:
        summary = df.groupby(group_by)[numeric_column].agg(["mean", "sum", "min", "max", "count"])
        return {"grouped_by": group_by, "summary": summary.round(2).to_dict(orient="index")}

    series = df[numeric_column]
    return {
        "mean": round(float(series.mean()), 2),
        "sum": round(float(series.sum()), 2),
        "min": round(float(series.min()), 2),
        "max": round(float(series.max()), 2),
        "count": int(series.count()),
    }
