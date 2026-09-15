from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.schemas import QueryRequest, AgentResponse
from app.services.agent_service import process_query
from app.exceptions import OutOfScopeError, LLMTimeoutError, LLMParsingError

app = FastAPI(title="Micro AI Agent")

@app.post("/analyze", response_model=AgentResponse)
def analyze(request: QueryRequest):
    try:
        result = process_query(request.user_query)
        return AgentResponse(success=True, data=result, message="Extraction successful.")
    except OutOfScopeError as e:
        return JSONResponse(
            status_code=200,
            content=AgentResponse(success=False, data=None, message=str(e)).model_dump(),
        )
    except LLMTimeoutError as e:
        return JSONResponse(
            status_code=503,
            content=AgentResponse(success=False, data=None, message=str(e)).model_dump(),
        )
    except LLMParsingError as e:
        return JSONResponse(
            status_code=422,
            content=AgentResponse(success=False, data=None, message=str(e)).model_dump(),
        )

@app.get("/")
def root():
    return {"status": "ok", "service": "Micro AI Agent"}