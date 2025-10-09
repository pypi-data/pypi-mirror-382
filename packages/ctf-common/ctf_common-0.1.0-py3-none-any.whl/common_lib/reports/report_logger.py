# report_logger.py
import logging
import traceback

from common_lib.reports.report_enums import LogLevel
from common_lib.reports.report_manager import ReportManager
import threading


logger = logging.getLogger(__name__)

class ReportLogger:

    def __init__(self):
        _running_steps = {}
        self._lock = threading.Lock()

    @staticmethod
    def info(message, step_info=None):
        logger.info(message)
        ReportManager.add_step_log(step_info, message, LogLevel.INFO)

    @staticmethod
    def success(message, step_info=None):
        logger.info(message)
        ReportManager.add_step_log(step_info, message, LogLevel.SUCCESS)

    @staticmethod
    def warn( message, step_info=None):
        logger.warning(message)
        ReportManager.add_step_log(step_info, message, LogLevel.WARNING)


    @staticmethod
    def error( message, step_info=None):
        logger.error(message)
        ReportManager.add_step_log(step_info, message, LogLevel.ERROR)


    @staticmethod
    def exception( message="", step_info=None):
        exception_info = traceback.format_exc()
        full_message = f"{message}\n{exception_info}" if message else exception_info
        logger.error(full_message)
        ReportManager.add_step_log(step_info, full_message, LogLevel.ERROR)




