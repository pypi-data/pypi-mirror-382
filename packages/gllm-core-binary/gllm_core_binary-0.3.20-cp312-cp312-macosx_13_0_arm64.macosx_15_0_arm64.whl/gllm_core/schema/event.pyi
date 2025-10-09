from datetime import datetime
from gllm_core.constants import EventLevel as EventLevel
from pydantic import BaseModel
from typing import Any

class Event(BaseModel):
    """A data class to store an event attributes.

    Attributes:
        value (str | dict[str, Any]): The value of the event.
        level (EventLevel): The severity level of the event. Defined through the EventLevel constants.
        type (str): The type of the event. Includes but are not limited to the EventType constants.
        timestamp (datetime): The timestamp of the event. If not provided, the current timestamp is used.
        metadata (dict[str, Any]): The metadata of the event. Defaults to an empty dictionary.
    """
    value: str | dict[str, Any]
    level: EventLevel
    type: str
    timestamp: datetime
    metadata: dict[str, Any]
    def serialize_level(self, level: EventLevel) -> str:
        """Serializes an EventLevel object into its string representation.

        This method serializes the given EventLevel object by returning its name as a string.

        Args:
            level (EventLevel): The EventLevel object to be serialized.

        Returns:
            str: The name of the EventLevel object.
        """
