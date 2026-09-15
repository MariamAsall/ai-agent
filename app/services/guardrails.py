import json
from app.schemas import ExtractedInfo
from app.exceptions import OutOfScopeError, LLMParsingError

def validate_input(user_query: str):
    if not user_query or len(user_query.strip()) < 3:
        raise OutOfScopeError("Query too short or empty.")

def parse_llm_output(raw_output: str) -> ExtractedInfo:
    try:
        data = json.loads(raw_output)
    except json.JSONDecodeError:
        raise LLMParsingError("LLM did not return valid JSON.")

    if data.get("intent", "").lower() in ["none", "unknown", "out_of_scope", ""]:
        raise OutOfScopeError("Query is out of scope for this agent.")

    try:
        return ExtractedInfo(**data)
    except Exception as e:
        raise LLMParsingError(f"Output doesn't match expected schema: {e}")