# Micro AI Agent with Guardrails
A lightweight FastAPI service that takes free-text customer support queries, extracts structured data through an LLM, and applies guardrails to prevent hallucinated or malformed output.

## Project Overview
| Item | Detail |
|---|---|
| Framework | FastAPI |
| LLM Provider | Groq (OpenAI-compatible API) |
| Model | `openai/gpt-oss-20b` |
| Validation | Pydantic v2 |
| Endpoints | 2 (`/analyze`, `/`) |
| Guardrails | Input length, out-of-scope detection, JSON schema validation |

The service handles the full request lifecycle:
- A user submits free-text input (e.g. a support message) via `POST /analyze`
- The input is validated before it ever reaches the LLM
- The LLM is prompted to return strict JSON matching a fixed schema
- The output is parsed and validated against that schema
- If the query is out of scope, or the LLM output is malformed, unusable, or the request times out, the API returns a clean fallback response instead of crashing or hallucinating

## Repository Structure
```
app/
├── __init__.py
├── main.py                   # FastAPI app, route, exception → HTTP status mapping
├── config.py                 # Env loading (GROQ_API_KEY, GROQ_MODEL, GROQ_BASE_URL)
├── schemas.py                 # Pydantic models: QueryRequest, ExtractedInfo, AgentResponse
├── exceptions.py              # Custom exceptions (OutOfScopeError, LLMTimeoutError, LLMParsingError, LLMServiceError)
├── services/
│   ├── __init__.py
│   ├── agent_service.py       # LLM call + orchestration
│   └── guardrails.py          # Input validation + output parsing/validation
└── tests/
    └── test_endpoint.py       # Endpoint tests: valid, out-of-scope, malformed input

requirements.txt
.env.example
.gitignore
README.md
```

## How It Works
### Request flow
1. **Input guardrail** (`guardrails.validate_input`) — rejects empty or too-short queries before spending a single token.
2. **LLM call** (`agent_service.process_query`) — sends the query to Groq with a system prompt that forces a fixed JSON schema and `intent: out_of_scope` for anything unrelated to customer support.
3. **Output guardrail** (`guardrails.parse_llm_output`) — strips markdown fences if present, parses JSON, checks it's an object (not a list/string), rejects `out_of_scope` intents, and validates the result against `ExtractedInfo`.
4. **Error mapping** (`main.py`) — every failure mode maps to a distinct, predictable HTTP response instead of an unhandled crash.

### Exception → HTTP status mapping
| Exception | Meaning | HTTP Status |
|---|---|---|
| `OutOfScopeError` | Query is empty, too short, or unrelated to support | 200 (`success: false`) |
| `LLMTimeoutError` | Request timed out or was rate-limited | 503 |
| `LLMParsingError` | LLM output wasn't valid JSON or didn't match the schema | 422 |
| `LLMServiceError` | Groq API returned a non-timeout error | 502 |
| Anything else | Unexpected error | 500 |

## API Reference
### `POST /analyze`
**Request**
```json
{
  "user_query": "Hi, I'm Ahmed and I need to cancel my booking for tomorrow, it's urgent."
}
```

**Response — success**
```json
{
  "success": true,
  "data": {
    "intent": "cancellation",
    "person_name": "Ahmed",
    "email": null,
    "phone_number": null,
    "urgency": "high",
    "summary": "Ahmed wants to cancel tomorrow's booking urgently."
  },
  "message": "Extraction successful."
}
```

**Response — guardrail caught an out-of-scope query**
```json
{
  "success": false,
  "data": null,
  "message": "Query is out of scope for this agent."
}
```

### `GET /`
Health check — returns `{"status": "ok", "service": "Micro AI Agent"}`.

## Getting Started
### Prerequisites
- Python 3.10+
- A Groq API key ([console.groq.com](https://console.groq.com))

### Setup
```bash
# 1. Clone and enter the repo
git clone <repo-url>
cd micro-ai-agent

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# then edit .env and set GROQ_API_KEY=your_key_here

# 5. Run the server
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000/docs` for the interactive Swagger UI.

### Testing the endpoint
**Via curl:**
```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"user_query": "I want to book a table for 4 people tonight, my email is ahmed@example.com"}'
```

**Testing the guardrail (out-of-scope input):**
```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"user_query": "what is the capital of France"}'
```

### Running the test suite
```bash
pytest app/tests/ -v
```
Covers: a valid extraction, an out-of-scope query, and a malformed/empty query.

## Tech Stack
FastAPI · Pydantic v2 · OpenAI Python SDK (pointed at Groq's OpenAI-compatible endpoint) · pytest

---
Micro AI Agent with Guardrails — Trial Task Submission