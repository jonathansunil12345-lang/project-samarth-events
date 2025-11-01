"""
Data Load Stage - Loads required datasets based on parsed query

This is the second stage in the event-driven pipeline.
Input: Parsed intent and parameters
Output: Loaded datasets
"""
from typing import Any
import logging
from .base_stage import PipelineStage
from ..data_manager import DataManager

logger = logging.getLogger(__name__)


class DataLoadStage(PipelineStage):
    """
    Loads data required for the query.

    Event Flow:
    - Listens to: 'query.parsed'
    - Publishes to: 'data.loaded'
    """

    def __init__(self, event_bus, data_manager: DataManager):
        """
        Initialize data load stage.

        Args:
            event_bus: Event bus instance
            data_manager: Data manager instance
        """
        self.data_manager = data_manager
        super().__init__(event_bus)

    def input_topic(self) -> str:
        return "query.parsed"

    def output_topic(self) -> str:
        return "data.loaded"

    def process(self, data: Any, metadata: dict) -> Any:
        """
        Load required datasets.

        Args:
            data: Dictionary with 'intent' and 'params'
            metadata: Event metadata

        Returns:
            Dictionary with loaded datasets
        """
        logger.info("Loading datasets for query")

        # Load both datasets (in real system, could be selective based on intent)
        agriculture_data = self.data_manager.load_dataset("agriculture")
        rainfall_data = self.data_manager.load_dataset("rainfall")

        result = {
            **data,  # Pass along the parsed data
            "datasets": {
                "agriculture": agriculture_data,
                "rainfall": rainfall_data
            }
        }

        logger.debug(f"Loaded {len(agriculture_data)} agriculture records, {len(rainfall_data)} rainfall records")
        return result
