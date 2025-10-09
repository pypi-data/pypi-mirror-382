"""公共枚举类型"""

from enum import Enum

class ResponseStatus(Enum):
    """响应状态枚举"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
