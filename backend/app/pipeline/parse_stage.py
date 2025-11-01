"""
Parse Stage - Converts natural language question to structured parameters

This is the first stage in the event-driven pipeline.
Input: Raw question string
Output: Parsed intent and parameters
"""
from typing import Any, Callable
import logging
from .base_stage import PipelineStage
from ..question_parser import parse_question

logger = logging.getLogger(__name__)


class ParseStage(PipelineStage):
    """
    Parses natural language questions into structured parameters.

    Event Flow:
    - Listens to: 'query.received'
    - Publishes to: 'query.parsed'
    """

    def __init__(self, event_bus, parser_fn: Callable):
        """
        Initialize parse stage.

        Args:
            event_bus: Event bus instance
            parser_fn: Question parser function
        """
        self.parser_fn = parser_fn
        super().__init__(event_bus)

    def input_topic(self) -> str:
        return "query.received"

    def output_topic(self) -> str:
        return "query.parsed"

    def process(self, data: Any, metadata: dict) -> Any:
        """
        Parse the question.

        Args:
            data: Dictionary with 'question' key
            metadata: Event metadata

        Returns:
            Dictionary with 'intent' and 'params'
        """
        question = data["question"]
        logger.info(f"Parsing question: {question}")

        # Parse the question
        parsed = self.parser_fn(question)

        result = {
            "question": question,
            "intent": parsed.intent,
            "params": parsed.params
        }

        logger.debug(f"Parsed intent: {parsed.intent}")
        return result
