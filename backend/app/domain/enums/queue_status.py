from enum import Enum


class QueueStatus(str, Enum):
    WAITING = "WAITING"
    CALLED = "CALLED"
    SEATED = "SEATED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"
