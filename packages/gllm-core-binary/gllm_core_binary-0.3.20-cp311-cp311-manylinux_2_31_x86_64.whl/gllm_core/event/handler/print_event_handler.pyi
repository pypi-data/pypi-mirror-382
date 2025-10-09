from _typeshed import Incomplete
from gllm_core.constants import EventType as EventType
from gllm_core.event.handler.event_handler import BaseEventHandler as BaseEventHandler
from gllm_core.schema import Event as Event

class TypeKey:
    """Defines the type keys for the events."""
    ACTIVITY: str
    CODE: str
    THINKING: str
    START_SUFFIX: str
    END_SUFFIX: str

DEFAULT_COLOR_MAP: Incomplete
DEFAULT_COLOR: str

class PrintEventHandler(BaseEventHandler):
    """An event handler that prints the event with human readable format.

    Attributes:
        name (str): The name assigned to the event handler.
        padding_char (str): The character to use for padding.
        color_map (dict[str, str]): The dictionary that maps certain event types to their
            corresponding colors in hex format.
        console (Console): The Rich Console object to use for printing.
    """
    padding_char: Incomplete
    color_map: Incomplete
    console: Incomplete
    def __init__(self, name: str | None = None, padding_char: str = '=', color_map: dict[str, str] | None = None, separator_length: int | None = None) -> None:
        '''Initializes a new instance of the PrintEventHandler class.

        Args:
            name (str, optional): The name assigned to the event handler. Defaults to the class name.
            padding_char (str, optional): The character to use for padding. Defaults to "=".
            color_map (dict[str, str], optional): The dictionary that maps certain event types to their
                corresponding colors in hex format. Defaults to None, in which case the default color map will be used.
            separator_length (int | None, optional): Deprecated parameter. Defaults to None.
        '''
    async def emit(self, event: Event) -> None:
        """Emits the given event.

        Args:
            event (Event): The event to be emitted.
        """
