import requests

_report_api_host = "http://127.0.0.1:8000/api"
_report_api_content_type = "application/json"

def create_run_instance(**kwargs):
    api = f'{_report_api_host}/run/create'
    return requests.post(api, json=kwargs, headers={"Content-Type": _report_api_content_type})


def update_run_instance(**kwargs):
    api = f'{_report_api_host}/run/update'
    return requests.post(api, json=kwargs, headers={"Content-Type": _report_api_content_type})


def create_test_case(**kwargs):
    api = f'{_report_api_host}/case/create'
    return requests.post(api, json=kwargs, headers={"Content-Type": _report_api_content_type})


def update_test_case(**kwargs):
    api = f'{_report_api_host}/case/update'
    return requests.post(api, json=kwargs, headers={"Content-Type": _report_api_content_type})


def create_test_step(**kwargs):
    api = f'{_report_api_host}/step/create'
    return requests.post(api, json=kwargs, headers={"Content-Type": _report_api_content_type})

def update_test_step(**kwargs):
    api = f'{_report_api_host}/step/update'
    return requests.post(api, json=kwargs, headers={"Content-Type": _report_api_content_type})


def add_step_log(**kwargs):
    api = f'{_report_api_host}/step/addLog'
    return requests.post(api, json=kwargs, headers={"Content-Type": _report_api_content_type})


if __name__ == "__main__":
    print("test")