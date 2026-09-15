from openai import OpenAI, APITimeoutError, APIError, RateLimitError
from app.config import GROQ_API_KEY, GROQ_MODEL, GROQ_BASE_URL
from app.services.guardrails import validate_input, parse_llm_output
from app.exceptions import LLMTimeoutError
from app.schemas import ExtractedInfo

client = OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)

SYSTEM_PROMPT = """You are a structured data extraction agent for customer support requests.
Given a user's message, extract the following as strict JSON only, no extra text:
{
  "intent": one of ["complaint", "inquiry", "booking", "cancellation", "out_of_scope"],
  "person_name": string or null,
  "email": string or null,
  "phone_number": string or null,
  "urgency": one of ["low", "medium", "high"],
  "summary": short one-sentence summary of the request
}
If the message is unrelated to customer support (random chit-chat, unrelated topics), set intent to "out_of_scope".
Return ONLY the JSON object, nothing else."""

def process_query(user_query: str) -> ExtractedInfo:
    validate_input(user_query)

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_query},
            ],
            temperature=0,
            max_tokens=500,
            timeout=10,
        )
    except RateLimitError:
        raise LLMTimeoutError("Rate limit exceeded. Please try again shortly.")
    except APITimeoutError:
        raise LLMTimeoutError("The request to the LLM timed out.")
    except APIError as e:
        raise LLMTimeoutError(f"LLM API error: {e}")

    raw_output = response.choices[0].message.content.strip()
    return parse_llm_output(raw_output)