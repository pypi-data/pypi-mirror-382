from enum import Enum


class InstanceStatus(str, Enum):
    """High level lifecycle states"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    TERMINATED = "terminated"
    ERROR = "error"
    UNKNOWN = "unknown"
