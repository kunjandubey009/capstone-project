"""
Tool 4/5: financial_calculator_tool

Real financial math (not an LLM guess): ROI, simple payback period, and NPV
over a series of projected annual cash flows.
"""
from agents import function_tool


@function_tool
def financial_calculator_tool(
    initial_investment: float,
    annual_cash_flows: list[float],
    discount_rate_pct: float = 8.0,
) -> dict:
    """Compute ROI, payback period, and NPV for a projected investment.

    Args:
        initial_investment: Upfront cost of the initiative.
        annual_cash_flows: Projected net cash inflow for each future year, in order.
        discount_rate_pct: Annual discount rate as a percentage, used for NPV.
    """
    total_returns = sum(annual_cash_flows)
    roi_pct = ((total_returns - initial_investment) / initial_investment) * 100 if initial_investment else 0.0

    # Simple (undiscounted) payback period in months.
    cumulative = 0.0
    payback_years = None
    for i, cf in enumerate(annual_cash_flows, start=1):
        cumulative += cf
        if cumulative >= initial_investment and payback_years is None:
            prior_cumulative = cumulative - cf
            fraction = (initial_investment - prior_cumulative) / cf if cf else 0
            payback_years = (i - 1) + fraction
    payback_months = round(payback_years * 12, 1) if payback_years is not None else None

    r = discount_rate_pct / 100.0
    npv = -initial_investment + sum(cf / ((1 + r) ** year) for year, cf in enumerate(annual_cash_flows, start=1))

    return {
        "roi_pct": round(roi_pct, 2),
        "payback_period_months": payback_months,
        "npv": round(npv, 2),
        "discount_rate_pct": discount_rate_pct,
    }
