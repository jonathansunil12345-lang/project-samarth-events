import asyncio
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import load_config
from .data_manager import DataManager
from .question_parser import parse_question
from .query_executor import QueryExecutor

logger = logging.getLogger(__name__)


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    tables: list
    citations: list
    debug: dict | None = None


app = FastAPI(title="Project Samarth Prototype", version="0.1.0")

# Configure CORS - allow all origins for public API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

config = load_config()
data_manager = DataManager(config)
executor = QueryExecutor(parse_question, data_manager)


@app.get("/")
def root():
    """Root endpoint for health checks."""
    return {"status": "ok", "service": "Project Samarth Prototype"}


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
    except asyncio.TimeoutError:
        logger.error("Query timed out after 30 seconds")
        raise HTTPException(
            status_code=504,
            detail="Query execution timed out. The request took too long to process. Please try a simpler question."
        )
    except ValueError as exc:
        logger.warning(f"Invalid request: {exc}")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Unexpected error processing query: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your query: {str(exc)}"
        ) from exc


@app.post("/refresh")
def refresh():
    """Refresh data from data.gov.in API."""
    data_manager.load_dataset("agriculture", force_refresh=True)
    data_manager.load_dataset("rainfall", force_refresh=True)
    return {"status": "reloaded"}
