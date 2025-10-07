from gllm_core.schema import Event
from gllm_inference.schema.activity import Activity as Activity
from gllm_inference.schema.enums import EmitDataType as EmitDataType
from typing import Literal

class ReasoningEvent(Event):
    """Event schema for model reasoning.

    Attributes:
        id (str): The unique identifier for the thinking event. Defaults to an UUID string.
        data_type (Literal): The type of thinking event (thinking, thinking_start, or thinking_end).
        data_value (str): The thinking content or message.
    """
    id: str
    data_type: Literal[EmitDataType.THINKING, EmitDataType.THINKING_START, EmitDataType.THINKING_END]
    data_value: str

class ActivityEvent(Event):
    """Event schema for model-triggered activities (e.g. web search, MCP).

    Attributes:
        id (str): The unique identifier for the activity event. Defaults to an UUID string.
        data_type (Literal): The type of event, always 'activity'.
        data_value (Activity): The activity data containing message and type.
    """
    id: str
    data_type: Literal[EmitDataType.ACTIVITY]
    data_value: Activity

class CodeEvent(Event):
    """Event schema for model-triggered code execution.

    Attributes:
        id (str): The unique identifier for the code event. Defaults to an UUID string.
        data_type (Literal): The type of event (code, code_start, or code_end).
        data_value (str): The code content.
    """
    id: str
    data_type: Literal[EmitDataType.CODE, EmitDataType.CODE_START, EmitDataType.CODE_END]
    data_value: str
