from enum import StrEnum

class LangflowEventType(StrEnum):
    """Enum for Langflow event types as received from the API."""
    ADD_MESSAGE = 'add_message'
    END = 'end'
    UNKNOWN = 'unknown'
