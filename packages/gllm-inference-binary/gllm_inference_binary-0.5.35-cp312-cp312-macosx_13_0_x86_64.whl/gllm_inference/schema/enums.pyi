from enum import StrEnum

class AttachmentType(StrEnum):
    """Defines valid attachment types."""
    AUDIO = 'audio'
    DOCUMENT = 'document'
    IMAGE = 'image'
    VIDEO = 'video'

class BatchStatus(StrEnum):
    """Defines the status of a batch job."""
    CANCELING = 'canceling'
    IN_PROGRESS = 'in_progress'
    FINISHED = 'finished'
    UNKNOWN = 'unknown'

class EmitDataType(StrEnum):
    """Defines valid data types for emitting events."""
    ACTIVITY = 'activity'
    CODE = 'code'
    CODE_START = 'code_start'
    CODE_END = 'code_end'
    THINKING = 'thinking'
    THINKING_START = 'thinking_start'
    THINKING_END = 'thinking_end'

class MessageRole(StrEnum):
    """Defines valid message roles."""
    SYSTEM = 'system'
    USER = 'user'
    ASSISTANT = 'assistant'

class TruncateSide(StrEnum):
    """Enumeration for truncation sides."""
    RIGHT = 'RIGHT'
    LEFT = 'LEFT'
