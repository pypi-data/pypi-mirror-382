import threading
import os
import getpass
from ctf_common.reports.report_enums import LogLevel, TestStatus
import ctf_common.reports.report_api as report_factory
from ctf_common.reports.report_data import RunResult, CaseResult, StepResult

_thread_local = threading.local()


class ReportManager:

    @staticmethod
    def create_test_run(**kwargs):
        project_lob = kwargs.get("lob") if kwargs.get("lob") is not None else os.getenv('PROJECT_LOB', 'UNKNOW')
        project_name = kwargs.get("project") if kwargs.get("project") is not None else os.getenv('PROJECT_NAME', "Auto")
        run_by = kwargs.get("test_by") if kwargs.get("test_by") is not None else os.getenv('TEST_RUN_BY',
                                                                                           os.getenv(
                                                                                               'HOST_USER') or getpass.getuser())
        test_scope = kwargs.get("scope_name") if kwargs.get("scope_name") is not None else os.getenv('TEST_SCOPE',
                                                                                                     'DEBUG')
        test_description = kwargs.get("description") if kwargs.get("description") is not None else os.getenv(
            'TEST_DESCRIPTION', 'Automation test')
        test_tags = kwargs.get("tags") if kwargs.get("tags") is not None else os.getenv('TEST_TAGS', None)
        test_case_count = kwargs.get("case_count") if kwargs.get("case_count") is not None else 0

        run_input = {
            "lob": project_lob,
            "projectName": project_name,
            "runBy": run_by,
            "testScope": test_scope,
            "description": test_description,
            "tags": test_tags,
            "caseCount": test_case_count
        }

        run_response = report_factory.create_run_instance(**run_input).json()
        run_result = RunResult()
        run_result.set_id(run_response.get("run_id"))

        return ReportManager._add_run_to_thread(run_result)

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

        case_response = report_factory.create_test_case(**case_info).json()
        case_result = CaseResult(None, run_instance_id)
        case_result.set_id(case_response.get("case_id"))

        return ReportManager._add_case_to_thread(case_result)

    @staticmethod
    def create_test_step(case_id, step_name):
        step_info = {
            "case_id": case_id,
            "step_name": step_name
        }
        step_response = report_factory.create_test_step(**step_info).json()
        step_result = StepResult(None, case_id)
        step_result.set_id(step_response.get("step_id"))

        return ReportManager._add_step_to_thread(step_result)

    @staticmethod
    def complete_test_case(case_result=None):
        if case_result is None:
            case_result = _thread_local.case_result
        case_info = {
            "case_id": case_result.id,
            "status": case_result.status,
            "highlights": case_result.highlights
        }
        response_json = report_factory.update_test_case(**case_info)
        case_result.status = response_json.get("status")
        run_result = _thread_local.run_result
        run_result.update_status(case_result.status)
        case_result.clear()

    @staticmethod
    def complete_test_step(step_result=None):
        if step_result is None:
            step_result = _thread_local.step_result

        if step_result and step_result.id:
            logs_dict_list = []
            for log in step_result.get_logs():
                logs_dict_list.append(log.to_dict())

            step_info = {
                "step_id": step_result.id,
                "status": step_result.status,
                "logs": logs_dict_list
            }
            try:
                response_json = report_factory.update_test_step(**step_info).json()
                print(response_json)
                step_result.status = response_json.get("status")
            except Exception as e:
                print(e)

            ReportManager.get_case().update_status(step_result.status)
            ReportManager.get_run().update_status(step_result.status)
            step_result.clear()

    @staticmethod
    def add_step_log(step_result, log, level):
        if step_result is None:
            step_result = ReportManager.get_step()
        if step_result and step_result.id:
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
