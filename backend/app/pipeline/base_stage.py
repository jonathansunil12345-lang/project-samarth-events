"""
Base Pipeline Stage

This is the TEMPLATE METHOD PATTERN:
- Base class defines the workflow
- Subclasses implement specific processing logic
"""
from abc import ABC, abstractmethod
from typing import Any
import logging
from ..event_bus import EventBus, Event

logger = logging.getLogger(__name__)


class PipelineStage(ABC):
    """
    Base class for all pipeline stages.

    Each stage:
    1. Subscribes to an input topic
    2. Processes the event data
    3. Publishes result to an output topic
    """

    def __init__(self, event_bus: EventBus):
        """
        Initialize pipeline stage.

        Args:
            event_bus: The event bus to subscribe/publish to
        """
        self.event_bus = event_bus
        self._register()

    def _register(self):
        """Register this stage with the event bus."""
        input_topic = self.input_topic()
        self.event_bus.subscribe(input_topic, self._handle_event)
        logger.info(f"{self.__class__.__name__} registered for topic '{input_topic}'")

    def _handle_event(self, event: Event):
        """
        Internal event handler that calls process() and publishes result.

        Args:
            event: Incoming event
        """
        logger.debug(f"{self.__class__.__name__} processing event from '{event.topic}'")

        try:
            # Process the event data
            result = self.process(event.data, event.metadata)

            # Publish to next stage
            output_topic = self.output_topic()
            self.event_bus.publish(
                topic=output_topic,
                data=result,
                metadata={
                    **event.metadata,
                    "processed_by": self.__class__.__name__
                }
            )
            logger.debug(f"{self.__class__.__name__} published to '{output_topic}'")

        except Exception as e:
            logger.error(f"{self.__class__.__name__} failed: {e}")
            # Publish error event
            self.event_bus.publish(
                topic="pipeline.error",
                data={"error": str(e), "stage": self.__class__.__name__},
                metadata=event.metadata
            )
            raise

    @abstractmethod
    def input_topic(self) -> str:
        """
        Return the topic this stage listens to.

        Returns:
            Topic name (e.g., 'query.parsed')
        """
        pass

    @abstractmethod
    def output_topic(self) -> str:
        """
        Return the topic this stage publishes to.

        Returns:
            Topic name (e.g., 'data.loaded')
        """
        pass

    @abstractmethod
    def process(self, data: Any, metadata: dict) -> Any:
        """
        Process the event data.

        Args:
            data: Event payload
            metadata: Event metadata

        Returns:
            Processed data to publish to next stage
        """
        pass
