"""
Event Bus - Central Pub/Sub System

This implements the OBSERVER PATTERN and PUB/SUB architecture:
- Events are published to the bus with a topic
- Subscribers listen to specific topics
- Decouples event producers from consumers
"""
from typing import Dict, List, Callable, Any
import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """
    Represents an event in the system.

    Attributes:
        topic: Event type (e.g., 'query.parsed', 'data.loaded', 'analysis.complete')
        data: Payload data
        timestamp: When the event occurred
        metadata: Additional context
    """
    topic: str
    data: Any
    timestamp: datetime = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}


class EventBus:
    """
    Central event bus for publish/subscribe communication.

    This enables loose coupling between pipeline stages:
    - Parser publishes 'query.parsed' events
    - Data loader subscribes to 'query.parsed' and publishes 'data.loaded'
    - Analyzer subscribes to 'data.loaded' and publishes 'analysis.complete'
    - Formatter subscribes to 'analysis.complete' and returns final result
    """

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_history: List[Event] = []
        self._max_history = 100  # Keep last 100 events for debugging

    def subscribe(self, topic: str, handler: Callable[[Event], None]):
        """
        Subscribe to events of a specific topic.

        Args:
            topic: Event topic to listen for (e.g., 'query.parsed')
            handler: Function to call when event is published
        """
        if topic not in self._subscribers:
            self._subscribers[topic] = []

        self._subscribers[topic].append(handler)
        logger.debug(f"Subscribed handler {handler.__name__} to topic '{topic}'")

    def publish(self, topic: str, data: Any, metadata: Dict[str, Any] = None):
        """
        Publish an event to all subscribers of the topic.

        Args:
            topic: Event topic (e.g., 'data.loaded')
            data: Event payload
            metadata: Additional context
        """
        event = Event(topic=topic, data=data, metadata=metadata or {})

        # Store in history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)

        # Notify subscribers
        if topic in self._subscribers:
            logger.debug(f"Publishing event '{topic}' to {len(self._subscribers[topic])} subscribers")
            for handler in self._subscribers[topic]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in handler {handler.__name__} for topic '{topic}': {e}")
                    raise
        else:
            logger.warning(f"No subscribers for topic '{topic}'")

    def get_event_history(self, topic: str = None) -> List[Event]:
        """
        Get event history, optionally filtered by topic.

        Args:
            topic: Optional topic to filter by

        Returns:
            List of events
        """
        if topic:
            return [e for e in self._event_history if e.topic == topic]
        return self._event_history.copy()

    def clear_subscribers(self):
        """Clear all subscriptions (useful for testing)."""
        self._subscribers.clear()
        logger.debug("Cleared all subscribers")


# Global event bus instance
event_bus = EventBus()
