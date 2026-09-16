from pydantic import BaseModel, Field
from typing import Optional

class QueryRequest(BaseModel):
    user_query: str = Field(..., min_length=1, max_length=1000, description="Raw user input text")

class ExtractedInfo(BaseModel):
    intent: str = Field(..., description="complaint, inquiry, booking, or cancellation")
    person_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    urgency: str = Field(..., description="low, medium, or high")
    summary: str

class AgentResponse(BaseModel):
    success: bool
    data: Optional[ExtractedInfo] = None
    message: str
