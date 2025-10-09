from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import threading
from common_lib.reports.report_enums import TestStatus
from common_lib.reports.data_log_entry import LogEntry



class TestResultBase:
    def __init__(self, id_value: Optional[str] = None, parent_id: Optional[str] = None):
        self._lock = threading.Lock()
        self.id = id_value
        self.status = TestStatus.RUNNING.value
        self.completed = False
        self.parent_id = parent_id
        self.start_time = datetime.now().isoformat()
        self.end_time = None

    def set_id(self, run_id):
        self.id = run_id

    def set_status(self, status: str):
        self.status = status

    def get_end_time(self):
        if self.end_time:
            return self.end_time
        else:
            self.end_time = datetime.now().isoformat()
            return self.end_time


    def update_status(self, new_status: str):
        with self._lock:
            if new_status == TestStatus.FAILED.value:
                self.status = TestStatus.FAILED.value
            elif new_status == TestStatus.RUNNING.value and self.status == TestStatus.WARN.value:
                self.status = TestStatus.WARN.value

    def clear(self):
        self.id = None
        self.status = None
        self.completed = False
        self.parent_id = None


@dataclass
class StepResult(TestResultBase):
    _logs: List[LogEntry] = field(default_factory=list)
    # case_id: Optional[str] = None

    def __init__(self, step_id, parent_id):
        super().__init__(step_id, parent_id)
        self._logs = []
        self._log_start = datetime.now()
        self._lock = threading.Lock()  # 为每个实例添加锁

    def is_save_result(self):
        return (datetime.now() - self._log_start).total_seconds() > 60*5

    def reset(self):
        self._log_start = datetime.now()
        self._logs = []

    def get_logs(self):
        return self._logs

    def set_logs(self, logs):
        self._logs = logs

    # @synchronized
    def append_logs(self, log, level):
        with self._lock:
            self.get_logs().append(LogEntry(level.value, log))


@dataclass
class CaseResult(TestResultBase):
    def __init__(self, case_id, parent_id):
        super().__init__(case_id, parent_id)
        self.highlights = []


@dataclass
class RunResult(TestResultBase):
    def __init__(self):
        super().__init__(None, None)
        self.description = ""