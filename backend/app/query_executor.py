"""
Query Executor - Coordinates the event-driven pipeline

This class:
1. Initializes all pipeline stages
2. Publishes the initial 'query.received' event
3. Waits for the 'response.ready' event
4. Returns the final result
"""
import asyncio
import logging
from typing import Dict, Any, Callable
from .event_bus import event_bus, Event
from .pipeline import ParseStage, DataLoadStage
from .pipeline.analysis_stage import AnalysisStage
from .pipeline.format_stage import FormatStage
from .question_parser import parse_question
from .data_manager import DataManager

logger = logging.getLogger(__name__)


class QueryExecutor:
    """
    Executes queries through the event-driven pipeline.

    Architecture:
    query.received → ParseStage → query.parsed
                                 ↓
                          DataLoadStage → data.loaded
                                          ↓
                                   AnalysisStage → analysis.complete
                                                   ↓
                                             FormatStage → response.ready
    """

    def __init__(self, parser_fn: Callable, data_manager: DataManager):
        """
        Initialize query executor and pipeline stages.

        Args:
            parser_fn: Question parser function
            data_manager: Data manager instance
        """
        self.parser_fn = parser_fn
        self.data_manager = data_manager
        self.result_future = None

        # Initialize pipeline stages (they auto-register with event bus)
        self.parse_stage = ParseStage(event_bus, parser_fn)
        self.data_stage = DataLoadStage(event_bus, data_manager)
        self.analysis_stage = AnalysisStage(event_bus)
        self.format_stage = FormatStage(event_bus)

        # Subscribe to final result
        event_bus.subscribe("response.ready", self._handle_result)
        event_bus.subscribe("pipeline.error", self._handle_error)

        logger.info("QueryExecutor initialized with all pipeline stages")

    def _handle_result(self, event: Event):
        """Handle the final result event."""
        if self.result_future and not self.result_future.done():
            self.result_future.set_result(event.data)

    def _handle_error(self, event: Event):
        """Handle pipeline error events."""
        if self.result_future and not self.result_future.done():
            error_msg = event.data.get("error", "Unknown error")
            self.result_future.set_exception(Exception(error_msg))

    async def execute_query(self, question: str) -> Dict[str, Any]:
        """
        Execute a query through the event-driven pipeline.

        Args:
            question: Natural language question

        Returns:
            Final formatted response

        Raises:
            asyncio.TimeoutError: If query times out
            Exception: If pipeline stage fails
        """
        logger.info(f"Executing query: {question}")

        # Create a future to wait for result
        loop = asyncio.get_event_loop()
        self.result_future = loop.create_future()

        # Publish initial event to start pipeline
        event_bus.publish(
            topic="query.received",
            data={"question": question},
            metadata={"source": "api"}
        )

        # Wait for result with timeout
        try:
            result = await asyncio.wait_for(self.result_future, timeout=30.0)
            logger.info("Query completed successfully")
            return result
        except asyncio.TimeoutError:
            logger.error("Query execution timed out")
            raise
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
