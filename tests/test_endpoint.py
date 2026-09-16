from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import ExtractedInfo
from app.exceptions import OutOfScopeError

client = TestClient(app)


def test_valid_query_returns_structured_data():
    """A well-formed, in-scope query should return success=True with populated fields."""
    fake_result = ExtractedInfo(
        intent="cancellation",
        person_name="Ahmed",
        email=None,
        phone_number=None,
        urgency="high",
        summary="Ahmed wants to cancel tomorrow's booking urgently.",
    )

    with patch("app.main.process_query", return_value=fake_result):
        response = client.post(
            "/analyze",
            json={"user_query": "Hi, I'm Ahmed and I need to cancel my booking for tomorrow, it's urgent."},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["intent"] == "cancellation"
    assert body["data"]["person_name"] == "Ahmed"
    assert body["data"]["urgency"] == "high"


def test_out_of_scope_query_is_caught_by_guardrail():
    """A query unrelated to customer support should be caught gracefully, not crash or hallucinate."""
    with patch("app.main.process_query", side_effect=OutOfScopeError("Query is out of scope for this agent.")):
        response = client.post(
            "/analyze",
            json={"user_query": "what is the capital of France"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert body["data"] is None
    assert "out of scope" in body["message"].lower()


def test_empty_query_is_rejected_by_request_validation():
    """An empty user_query should fail Pydantic's request validation (min_length=1) before reaching the LLM."""
    response = client.post(
        "/analyze",
        json={"user_query": ""},
    )

    # This 422 comes from FastAPI/Pydantic request validation, not from LLMParsingError -
    # the LLM is never called for a request this malformed.
    assert response.status_code == 422
