from dataclasses import dataclass, field
from typing import List, Dict, Protocol, Any


@dataclass
class Constraints:
    min_emergency_fund_months: int
    focus_debt_reduction: bool
    risk_tolerance: str
    priority_order: List[str] = field(default_factory=list)
    time_horizon_months: int = 12
    must_avoid: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)


@dataclass
class PlanAction:
    type: str
    amount: int
    requires_human_approval: bool = False


@dataclass
class Plan:
    name: str
    score: int
    actions: List[PlanAction]


@dataclass
class DemoResult:
    constraints: Constraints
    plans: List[Plan]
    markdown: str
    meta: Dict[str, Any] = field(default_factory=dict)


class GoalParser(Protocol):
    def parse(self, text: str, user: dict) -> Constraints: ...


class PlanExplainer(Protocol):
    def explain(
        self, plans: List[Plan], user: dict, constraints: Constraints
    ) -> str: ...
