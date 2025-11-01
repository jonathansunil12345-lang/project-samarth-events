from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import load_config
from .data_manager import DataManager
from .question_parser import parse_question
from .query_executor import QueryExecutor


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    tables: list
    citations: list
    debug: dict | None = None


app = FastAPI(title="Project Samarth Prototype", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

config = load_config()
data_manager = DataManager(config)
executor = QueryExecutor(parse_question, data_manager)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
async def ask(payload: AskRequest):
    """
    Process a natural language question using the event-driven pipeline.

    The QueryExecutor orchestrates the entire pipeline through events:
    1. question.received -> Parse Stage
    2. query.parsed -> Data Stage
    3. data.loaded -> Analysis Stage
    4. analysis.complete -> Format Stage
    5. response.ready -> Return to user
    """
    try:
        result = await executor.execute_query(payload.question)
        return AskResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/refresh")
def refresh():
    """Refresh data from data.gov.in API."""
    data_manager.load_dataset("agriculture", force_refresh=True)
    data_manager.load_dataset("rainfall", force_refresh=True)
    return {"status": "reloaded"}
