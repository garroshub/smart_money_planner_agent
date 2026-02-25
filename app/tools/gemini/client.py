import json
from typing import Any

try:
    from google import genai
    from google.genai import types
except ImportError:  # pragma: no cover - optional dependency
    genai = None
    types = None


class GeminiClient:
    def __init__(
        self,
        api_key: str,
        model: str,
        timeout_seconds: int = 20,
        temperature: float = 0.2,
    ):
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.temperature = temperature
        self.is_configured = bool(api_key)
        if self.is_configured and genai is None:
            raise RuntimeError(
                "google-genai is not installed. Install it to enable Agent mode."
            )
        self.client = genai.Client(api_key=api_key) if self.is_configured else None

    def parse_constraints(self, goals_text: str, user: dict) -> dict[str, Any]:
        if not self.is_configured:
            raise RuntimeError("Gemini client not configured.")

        schema = {
            "type": "OBJECT",
            "required": [
                "min_emergency_fund_months",
                "focus_debt_reduction",
                "risk_tolerance",
                "priority_order",
                "time_horizon_months",
                "must_avoid",
                "conflicts",
            ],
            "properties": {
                "min_emergency_fund_months": {"type": "INTEGER"},
                "focus_debt_reduction": {"type": "BOOLEAN"},
                "risk_tolerance": {"type": "STRING"},
                "priority_order": {"type": "ARRAY", "items": {"type": "STRING"}},
                "time_horizon_months": {"type": "INTEGER"},
                "must_avoid": {"type": "ARRAY", "items": {"type": "STRING"}},
                "conflicts": {"type": "ARRAY", "items": {"type": "STRING"}},
            },
        }

        prompt = (
            "Extract structured constraints from the goals text. "
            "Return JSON only, matching the schema. "
            "Use the user's risk_tolerance when goals are ambiguous.\n\n"
            f"User: {user}\n"
            f"Goals: {goals_text}"
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
                temperature=self.temperature,
            ),
        )

        if not response or not response.text:
            raise RuntimeError("Gemini returned empty constraints.")

        return json.loads(response.text)

    def explain_report(self, report_input: dict[str, Any]) -> str:
        if not self.is_configured:
            raise RuntimeError("Gemini client not configured.")

        prompt = (
            "Write a concise financial planning report in Markdown. "
            "Include headings: Overview, Plans, Recommendation, Risks. "
            "Use data from the input. Keep it professional and concrete.\n\n"
            f"Input: {json.dumps(report_input, indent=2)}"
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=self.temperature,
            ),
        )

        if not response or not response.text:
            raise RuntimeError("Gemini returned empty report.")

        return response.text
