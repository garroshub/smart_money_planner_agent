from pathlib import Path
import html
import re
import sys
from typing import Any

try:
    import pandas as pd
except ImportError:  # pragma: no cover
    pd = None

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from app.data.loader import load_users, load_accounts, load_goals
from app.agent.orchestrator import OrchestratorAgent
from app.config import get_config
from app.report_render import parse_report_blocks


GOAL_TEMPLATES = [
    "Pay off high-interest debt first while keeping a minimum emergency buffer.",
    "Increase long-term investments but avoid large monthly drawdown risk.",
    "Build a 6-month emergency fund before increasing discretionary spending.",
    "Stabilize cash flow, reduce monthly obligations, and avoid new debt.",
]


def as_currency(value: float) -> str:
    return f"${value:,.0f}"


def sum_debt(accounts: dict) -> float:
    return sum(item.get("balance", 0) for item in accounts.get("debts", []))


def sum_investments(accounts: dict) -> float:
    return sum(item.get("balance", 0) for item in accounts.get("investments", []))


def min_payments(accounts: dict) -> float:
    return sum(item.get("min_payment", 0) for item in accounts.get("debts", []))


def weighted_apr(accounts: dict) -> float:
    debts = [item for item in accounts.get("debts", []) if item.get("balance", 0) > 0]
    total = sum(item.get("balance", 0) for item in debts)
    if total <= 0:
        return 0.0
    weighted = sum(item.get("balance", 0) * item.get("apr", 0) for item in debts)
    return weighted / total


def get_goal_library(user_id: str, all_goals: list[dict[str, str]]) -> list[str]:
    goals = [item["goals_text"] for item in all_goals if item["user_id"] == user_id]
    merged = goals + GOAL_TEMPLATES
    deduped = []
    seen = set()
    for text in merged:
        if text not in seen:
            seen.add(text)
            deduped.append(text)
    return deduped


def get_action_amount(plan: Any, action_type: str) -> int:
    action = next((item for item in plan.actions if item.type == action_type), None)
    return int(action.amount) if action else 0


def build_plan_rows(result: Any, monthly_disposable: float) -> list[dict[str, Any]]:
    rows = []
    for plan in result.plans:
        emergency = get_action_amount(plan, "Emergency fund")
        debt = get_action_amount(plan, "Debt payment")
        invest = get_action_amount(plan, "Invest")
        total_alloc = emergency + debt + invest
        approvals = sum(1 for item in plan.actions if item.requires_human_approval)
        utilization = (
            (total_alloc / monthly_disposable * 100) if monthly_disposable > 0 else 0
        )
        rows.append(
            {
                "Plan": plan.name,
                "Score": plan.score,
                "Emergency": emergency,
                "Debt": debt,
                "Invest": invest,
                "Allocation total": total_alloc,
                "Budget utilization %": round(utilization, 1),
                "Approval-required actions": approvals,
            }
        )
    return rows


def pick_recommendation(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {}
    sorted_rows = sorted(
        rows,
        key=lambda row: (row["Score"], row["Debt"], row["Emergency"], row["Invest"]),
        reverse=True,
    )
    return sorted_rows[0]


def style_plan_table(
    rows: list[dict[str, Any]],
    recommended_plan_name: str | None,
):
    if pd is None:
        return rows

    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame

    if recommended_plan_name and recommended_plan_name in frame["Plan"].values:
        highlight_idx = frame.index[frame["Plan"] == recommended_plan_name][0]
    else:
        highlight_idx = frame["Score"].astype(float).idxmax()

    def row_style(row):
        if row.name == highlight_idx:
            return [
                "background-color: #fff4d6",
                "color: #1a1a1a",
                "border-top: 2px solid #e6a700",
                "border-bottom: 2px solid #e6a700",
                "font-weight: 600",
            ]
        return [""] * len(row)

    return frame.style.apply(row_style, axis=1)


def chart_allocation(rows: list[dict[str, Any]]) -> dict[str, list[Any]]:
    return {
        "Plan": [row["Plan"] for row in rows],
        "Emergency": [row["Emergency"] for row in rows],
        "Debt": [row["Debt"] for row in rows],
        "Invest": [row["Invest"] for row in rows],
    }


def chart_balance_sheet(user: dict, accounts: dict) -> dict[str, list[Any]]:
    debts = sum_debt(accounts)
    investments = sum_investments(accounts)
    cash = accounts.get("cash", 0)
    return {
        "Category": ["Cash", "Investments", "Debt"],
        "Amount": [cash, investments, debts],
    }


def chart_debt_stress(accounts: dict) -> list[dict[str, Any]]:
    rows = []
    for debt in accounts.get("debts", []):
        rows.append(
            {
                "Debt": debt.get("type", "unknown"),
                "Balance": debt.get("balance", 0),
                "APR %": round(debt.get("apr", 0) * 100, 2),
                "Min payment": debt.get("min_payment", 0),
            }
        )
    return rows


def normalize_goal_text(text: str) -> str:
    compact = re.sub(r"[ \t]+", " ", (text or "").strip())
    compact = re.sub(r"\n{3,}", "\n\n", compact)
    return compact


def validate_goal_text(text: str, mode: str, config: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    normalized = normalize_goal_text(text)
    min_chars = int(config.get("goals_min_chars", 20))
    max_chars = int(config.get("goals_max_chars", 400))
    max_lines = int(config.get("goals_max_lines", 5))

    if len(normalized) < min_chars:
        errors.append(f"Goals text must be at least {min_chars} characters.")
    if len(normalized) > max_chars:
        errors.append(f"Goals text must be {max_chars} characters or fewer.")
    if normalized.count("\n") >= max_lines:
        errors.append(f"Goals text must be {max_lines} lines or fewer.")
    if config.get("goals_block_urls", True) and re.search(
        r"https?://|www\.", normalized, re.IGNORECASE
    ):
        errors.append("Do not include URLs in goals text.")
    if config.get("goals_block_emails", True) and re.search(
        r"[\w.+-]+@[\w-]+\.[\w.-]+", normalized
    ):
        errors.append("Do not include email addresses in goals text.")
    if config.get("goals_block_phones", True) and re.search(
        r"\b\+?\d[\d\s\-()]{7,}\d\b", normalized
    ):
        errors.append("Do not include phone numbers in goals text.")
    if config.get("goals_block_guarantees", True) and re.search(
        r"\b(risk-free|guarantee|guaranteed|certain return)\b",
        normalized,
        re.IGNORECASE,
    ):
        errors.append(
            "Avoid guarantee-style claims (risk-free, guaranteed, certain return)."
        )
    if (
        mode == "agent"
        and config.get("goals_block_markdown", True)
        and re.search(r"[#`]|^\s*[-*]\s", normalized, re.MULTILINE)
    ):
        errors.append("Do not paste markdown syntax into goals text.")
    return errors


def render_plain_report(markdown_text: str) -> None:
    for block in parse_report_blocks(markdown_text):
        if block["type"] == "heading":
            level = max(2, min(3, int(block.get("level", 2))))
            st.markdown(f"{'#' * level} {block['text']}")
            continue

        if block["type"] == "plan_table":
            st.table(block["rows"])
            continue

        if block["type"] == "paragraph":
            st.markdown(f"<p>{html.escape(block['text'])}</p>", unsafe_allow_html=True)
            continue

        if block["type"] == "bullets":
            items = "".join(f"<li>{html.escape(item)}</li>" for item in block["items"])
            st.markdown(f"<ul>{items}</ul>", unsafe_allow_html=True)


def build_projection(
    account: dict,
    recommendation: dict[str, Any],
    months: int = 12,
) -> dict[str, list[float]]:
    emergency = float(account.get("cash", 0))
    debt = float(sum_debt(account))
    invest = float(sum_investments(account))

    emergency_add = float(recommendation.get("Emergency", 0))
    debt_add = float(recommendation.get("Debt", 0))
    invest_add = float(recommendation.get("Invest", 0))

    series = {
        "Emergency fund": [],
        "Debt balance": [],
        "Investments": [],
        "Net worth": [],
    }

    for _ in range(months):
        emergency += emergency_add
        debt = max(0.0, debt - debt_add)
        invest += invest_add
        net_worth = emergency + invest - debt

        series["Emergency fund"].append(emergency)
        series["Debt balance"].append(debt)
        series["Investments"].append(invest)
        series["Net worth"].append(net_worth)

    return series


st.set_page_config(page_title="Smart Money Planner", layout="wide")
st.title("Smart Money Planner (Local Demo)")

users = load_users()
accounts = load_accounts()
goals = load_goals()
accounts_by_user = {a["user_id"]: a for a in accounts}

config = get_config()

with st.sidebar:
    modes = ["rules"] if not config["agent_enabled"] else ["rules", "agent"]
    mode = st.selectbox("Mode", modes)
    if not config["agent_enabled"]:
        st.warning("Agent mode requires GEMINI_API_KEY.")
    user_ids = [u["id"] for u in users]
    user_id = st.selectbox("Persona", user_ids)
    user = next(u for u in users if u["id"] == user_id)
    user_goals = get_goal_library(user_id, goals)
    sample_goal = st.selectbox("Sample goals", user_goals or [""])
    if st.button("Load sample"):
        st.session_state["goals_text"] = sample_goal

goals_text = st.text_area(
    "Goals text",
    value=(st.session_state.get("goals_text") or sample_goal or ""),
    height=130,
    help=(
        f"Use {config['goals_min_chars']}-{config['goals_max_chars']} characters, "
        f"max {config['goals_max_lines']} lines."
    ),
)
run = st.button("Run demo")

mode_hint = "Deterministic rules only." if mode == "rules" else "Agent mode (Gemini)."
st.caption(mode_hint)

if run:
    if mode == "agent" and not config["agent_enabled"]:
        st.error("Agent mode is not configured. Set GEMINI_API_KEY and try again.")
        st.stop()

    cleaned_goals_text = normalize_goal_text(goals_text)
    validation_errors = validate_goal_text(cleaned_goals_text, mode, config)
    if validation_errors:
        st.error("Input validation failed:")
        for item in validation_errors:
            st.write(f"- {item}")
        st.stop()

    agent = OrchestratorAgent(config=config)
    account = accounts_by_user.get(user_id, {"cash": 0, "debts": [], "investments": []})
    result = agent.run(
        mode,
        user,
        account,
        cleaned_goals_text,
    )

    monthly_income = float(user.get("income_monthly", 0))
    monthly_expenses = float(user.get("expenses_monthly", 0))
    monthly_disposable = monthly_income - monthly_expenses
    cash = float(account.get("cash", 0))
    debt_total = float(sum_debt(account))
    investment_total = float(sum_investments(account))
    min_payment_total = float(min_payments(account))
    emergency_target = monthly_expenses * float(
        result.constraints.min_emergency_fund_months
    )
    emergency_progress = (
        (cash / emergency_target * 100) if emergency_target > 0 else 100.0
    )
    net_worth = cash + investment_total - debt_total

    trace = (
        f"Mode: `{mode}` | Provider: `{('gemini' if mode == 'agent' else 'rules')}` "
        f"| Parser: `{('RuleGoalParser' if mode == 'rules' else 'GeminiGoalParser')}` "
        f"| Explainer: `{('RulePlanExplainer' if mode == 'rules' else 'GeminiPlanExplainer')}`"
    )
    st.info(trace)

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    with k1:
        st.metric("Net worth", as_currency(net_worth))
    with k2:
        st.metric("Monthly cash flow", as_currency(monthly_disposable))
    with k3:
        st.metric("Emergency target", as_currency(emergency_target))
    with k4:
        st.metric("Emergency progress", f"{emergency_progress:.0f}%")
    with k5:
        st.metric("Debt total", as_currency(debt_total))
    with k6:
        st.metric("Weighted APR", f"{weighted_apr(account) * 100:.2f}%")

    st.caption(
        f"Minimum monthly debt payments: {as_currency(min_payment_total)} | "
        f"Risk tolerance: {result.constraints.risk_tolerance}"
    )

    plan_rows = build_plan_rows(result, monthly_disposable)
    recommendation = pick_recommendation(plan_rows)

    st.subheader("Plan comparison")
    if plan_rows:
        styled_plan_table = style_plan_table(plan_rows, recommendation.get("Plan"))
        st.dataframe(styled_plan_table, use_container_width=True, hide_index=True)
    else:
        st.dataframe(plan_rows, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("Allocation by plan")
        st.bar_chart(chart_allocation(plan_rows), x="Plan")
    with c2:
        st.subheader("Balance sheet")
        st.bar_chart(chart_balance_sheet(user, account), x="Category")
    with c3:
        st.subheader("Debt stress")
        debt_rows = chart_debt_stress(account)
        if debt_rows:
            st.bar_chart(debt_rows, x="Debt", y="Balance")
            st.dataframe(debt_rows, use_container_width=True)
        else:
            st.success("No active debt accounts for this persona.")

    st.subheader("Recommendation")
    if recommendation:
        st.markdown(
            "\n".join(
                [
                    f"**Recommended plan:** {recommendation['Plan']} (score {recommendation['Score']})",
                    f"- This plan allocates {as_currency(recommendation['Allocation total'])} per month and uses {recommendation['Budget utilization %']}% of current disposable cash flow.",
                    f"- Monthly split: Emergency {as_currency(recommendation['Emergency'])}, Debt {as_currency(recommendation['Debt'])}, Invest {as_currency(recommendation['Invest'])}.",
                    "- Prioritize approval-required actions first, then schedule automatic transfers for recurring items.",
                ]
            )
        )
    else:
        st.warning("No plans were generated for this input.")

    st.subheader("Assumptions and scenario outlook")
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        st.metric("Projection horizon", "12 months")
    with a2:
        st.metric("Income growth assumption", "0.0%")
    with a3:
        st.metric("Inflation assumption", "3.0%")
    with a4:
        st.metric("Rate assumption", "APR unchanged")

    if recommendation:
        projection = build_projection(account, recommendation, months=12)
        p1, p2 = st.columns(2)
        with p1:
            st.caption("Projected balances under current plan assumptions")
            st.line_chart(
                {
                    "Emergency fund": projection["Emergency fund"],
                    "Debt balance": projection["Debt balance"],
                    "Investments": projection["Investments"],
                }
            )
        with p2:
            st.caption("Projected net worth trajectory")
            st.area_chart({"Net worth": projection["Net worth"]})

    details_1, details_2 = st.tabs(["Narrative", "Raw data"])
    with details_1:
        render_plain_report(result.markdown)
    with details_2:
        st.json(
            {
                "constraints": result.constraints.__dict__,
                "plans": [
                    {
                        "name": p.name,
                        "score": p.score,
                        "actions": [a.__dict__ for a in p.actions],
                    }
                    for p in result.plans
                ],
            }
        )
