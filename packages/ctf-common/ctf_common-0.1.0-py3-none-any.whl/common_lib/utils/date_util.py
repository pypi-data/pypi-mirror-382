"""日期工具类"""

from datetime import datetime
from typing import Optional

def format_date(date_obj: datetime, format_str: str = "%Y-%m-%d") -> str:
    """格式化日期"""
    return date_obj.strftime(format_str)

def parse_date(date_str: str, format_str: str = "%Y-%m-%d") -> datetime:
    """解析日期字符串"""
    return datetime.strptime(date_str, format_str)
