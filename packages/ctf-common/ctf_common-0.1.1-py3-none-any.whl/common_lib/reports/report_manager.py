import threading

from common_lib.reports.report_enums import LogLevel, TestStatus
import common_lib.reports.report_api as report_factory

_thread_local = threading.local()


class ReportManager:

    @staticmethod
    def create_test_run(**kwargs):
        return ReportManager._add_run_to_thread(report_factory.create_run_instance(**kwargs))

    @staticmethod
    def complete_test_run(run_result=None):
        if run_result is None:
            run_result = _thread_local.run_result
        run_info = {
            "run_id": run_result.id,
            "status": run_result.status,
            "description": run_result.description
        }
        report_factory.update_run_instance(**run_info)
        run_result.update_status(run_result.status)
        run_result.clear()

    @staticmethod
    def create_test_case(run_instance_id, case_name, **kwargs):
        case_info = {
            "run_id": run_instance_id,
            "case_name": case_name,
            "case_jira_id": kwargs.get("case_jira_id", ""),
            "feature": kwargs.get("feature", ""),
            "comments": kwargs.get("comments", "")
        }

        return ReportManager._add_case_to_thread(
            report_factory.create_test_case(**case_info))

    @staticmethod
    def create_test_step(case_id, step_name):
        step_info = {
            "case_id": case_id,
            "step_name": step_name
        }
        return ReportManager._add_step_to_thread(
            report_factory.create_test_step(**step_info))

    @staticmethod
    def complete_test_case(case_result=None):
        if case_result is None:
            case_result = _thread_local.case_result
        case_info = {
            "case_id": case_result.id,
            "status": case_result.status,
            "comments": case_result.comments,
            "highlights": case_result.highlights
        }
        report_factory.update_test_case(**case_info)
        run_result = _thread_local.run_result
        run_result.update_status(case_result.status)
        case_result.clear()

    @staticmethod
    def complete_test_step(step_result=None):
        if step_result is None:
            step_result = _thread_local.step_result

        step_info = {
            "step_id": step_result.id,
            "status": step_result.status,
            "logs": step_result.get_logs()
        }
        report_factory.update_test_step(**step_info)
        ReportManager.get_case().update_status(step_result.status)
        ReportManager.get_run().update_status(step_result.status)
        step_result.clear()

    @staticmethod
    def add_step_log(step_result, log, level):
        if step_result is None:
            step_result = ReportManager.get_step()
        if step_result:
            step_result.append_logs(log, level)
            if level == LogLevel.ERROR:
                step_result.update_status(TestStatus.FAILED.value)
                ReportManager.get_case().update_status(TestStatus.FAILED.value)
                ReportManager.get_run().update_status(TestStatus.FAILED.value)
            elif level == LogLevel.WARNING:
                step_result.update_status(TestStatus.WARN.value)
                ReportManager.get_case().update_status(TestStatus.WARN.value)
                ReportManager.get_run().update_status(TestStatus.WARN.value)


            if step_result.is_save_result():
                step_info = {
                    "step_id": step_result.id,
                    "status": step_result.status,
                    "logs": step_result.get_
                 }
                report_factory.add_step_log(**step_info)

    @staticmethod
    def _add_run_to_thread(run_result):
        _thread_local.run_result = run_result
        return run_result

    @staticmethod
    def _add_case_to_thread(case_result):
        _thread_local.case_result = case_result
        return case_result

    @staticmethod
    def _add_step_to_thread(step_result):
        _thread_local.step_result = step_result
        return step_result

    @staticmethod
    def get_step():
        if not hasattr(_thread_local, "step_result"):
            return None
        return _thread_local.step_result

    @staticmethod
    def get_case():
        if not hasattr(_thread_local, "case_result"):
            return None
        return _thread_local.case_result

    @staticmethod
    def get_run():
        if not hasattr(_thread_local, "run_result"):
            return None
        return _thread_local.run_result
