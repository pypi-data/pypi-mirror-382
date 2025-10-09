from datetime import datetime
from typing import Optional


class LogEntry:
    def __init__(
            self,
            type: str,  # 'info' | 'error' | 'warning' | 'success'
            message: str,
            timestamp: Optional[str] = None
    ):
        valid_types = ['info', 'error', 'warning', 'success']
        if type not in valid_types:
            raise ValueError(f"Type must be one of {valid_types}")

        self.type = type
        self.message = message
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "message": self.message,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'LogEntry':
     
        return cls(
            type=data.get("type"),
            message=data.get("message"),
            timestamp=data.get("timestamp")
        )

    def __str__(self) -> str:
        return f"LogEntry(type='{self.type}', message='{self.message}', timestamp='{self.timestamp}')"

    def __repr__(self) -> str:
        return self.__str__()
