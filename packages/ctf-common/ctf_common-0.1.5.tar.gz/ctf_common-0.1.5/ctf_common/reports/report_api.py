import requests
import os
from ctf_common.constants.service_constants import REPORT_API_HOST_DEFAULT,REPORT_API_HOST_ENV_NAME

def create_run_instance(**kwargs):
    api = f'{get_report_host()}/run/create'
    return requests.post(api, json=kwargs, headers=get_headers())


def update_run_instance(**kwargs):
    api = f'{get_report_host()}/run/update'
    return requests.post(api, json=kwargs, headers=get_headers())


def create_test_case(**kwargs):
    api = f'{get_report_host()}/case/create'
    return requests.post(api, json=kwargs, headers=get_headers())


def update_test_case(**kwargs):
    api = f'{get_report_host()}/case/update'
    return requests.post(api, json=kwargs, headers=get_headers())


def create_test_step(**kwargs):
    api = f'{get_report_host()}/step/create'
    return requests.post(api, json=kwargs, headers=get_headers())

def update_test_step(**kwargs):
    api = f'{get_report_host()}/step/update'
    return requests.post(api, json=kwargs, headers=get_headers())

def add_step_log(**kwargs):
    api = f'{get_report_host()}/step/addLog'
    return requests.post(api, json=kwargs, headers=get_headers())

def get_report_host():
    return os.environ.get(REPORT_API_HOST_ENV_NAME, REPORT_API_HOST_DEFAULT)

def get_headers():
    return {"Content-Type": "application/json"}

if __name__ == "__main__":
    print("test")