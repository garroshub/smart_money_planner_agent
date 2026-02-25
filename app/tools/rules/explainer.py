from app.tools.interfaces import Plan, Constraints


class RulePlanExplainer:
    def explain(self, plans: list[Plan], user: dict, constraints: Constraints) -> str:
        blocks = []
        for i, plan in enumerate(plans, start=1):
            actions = "\n".join(
                f"- {a.type}: {a.amount}{' (approval required)' if a.requires_human_approval else ''}"
                for a in plan.actions
            )
            blocks.append(
                "\n".join(
                    [
                        f"### Plan {i} ({plan.name})",
                        f"**Score:** {plan.score}",
                        "**This month:**",
                        actions,
                        "**Why:**",
                        f"- Priority: {'debt reduction' if constraints.focus_debt_reduction else 'balanced'}",
                        f"- Risk tolerance: {constraints.risk_tolerance}",
                        "",
                    ]
                )
            )
        return "\n".join(blocks)
