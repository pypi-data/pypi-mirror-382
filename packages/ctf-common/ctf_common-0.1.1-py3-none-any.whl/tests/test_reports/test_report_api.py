from common_lib.reports.report_api import create_run_instance, update_run_instance, create_test_case
import pytest

# @pytest.mark.api
def test_create_run_api():
    run_input = {
        "lob": "EF",
        "projectName": "EF",
        "runBy": "joanne",
        "testScope": "Debug",
        "description": "test api"
    }
    run_result = create_run_instance(**run_input)
    print(run_result.json())

# @pytest.mark.api
def test_update_run_api():
    run_input = {
        "run_id": "68e3ad213f1cbe18de818d66",
        "status": "PASSED",
        "description": "test api"
    }
    run_result = update_run_instance(**run_input)
    print(run_result.json())
    assert run_result.status_code == 200

def test_create_case_api():
    case_input = {
        "run_id": "68e3ad213f1cbe18de818d66",
        "case_name": "test case",
        "case_jira_id": "",
        "feature": "",
        "comments": ""
    }

    case_result = create_test_case(**case_input)
    print(case_result.json())
    assert case_result.status_code == 200

