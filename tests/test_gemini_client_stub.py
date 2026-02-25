from app.tools.gemini.client import GeminiClient


def test_gemini_client_requires_key():
    client = GeminiClient(api_key="", model="gemini-3-flash-preview")
    assert client.is_configured is False
