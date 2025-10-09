from enum import Enum


class TestStatus(Enum):
    """
    Enum representing different test execution statuses
    """
    NOT_STARTED = "NOT STARTED"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    PASSED = "PASSED"
    WARN = "WARN"

    def __str__(self):
        return self.value

class LogLevel(Enum):
    """
    Enum representing different log levels
    """
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"