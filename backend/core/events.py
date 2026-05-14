<![CDATA["""
Thought Collision Engine — Event Bus
Simple asynchronous Pub/Sub Event Bus for decoupled event emission and handling.
"""
import asyncio
from typing import Callable, Awaitable, Any
from loguru import logger

class EventBus:
    def __init__(self):
        self._subscribers: dict[str, list[Callable[[str, Any], Awaitable[None]]]] = {}

    def subscribe(self, topic: str, handler: Callable[[str, Any], Awaitable[None]]):
        """Subscribe to an event topic."""
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(handler)
        logger.debug("Subscribed to topic: {}", topic)

    async def publish(self, topic: str, payload: Any):
        """Publish an event to a topic."""
        logger.debug("Publishing event on topic: {}", topic)
        handlers = self._subscribers.get(topic, [])
        # Match wildcard topics like 'ingestion.*'
        for registered_topic, registered_handlers in self._subscribers.items():
            if registered_topic.endswith(".*"):
                prefix = registered_topic[:-2]
                if topic.startswith(prefix) and registered_topic != topic:
                    handlers.extend(registered_handlers)

        if not handlers:
            return

        # Execute handlers concurrently
        tasks = [handler(topic, payload) for handler in handlers]
        await asyncio.gather(*tasks, return_exceptions=True)

event_bus = EventBus()
]]>
