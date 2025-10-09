from ctf_common.reports.report_logger import ReportLogger


class CompareLogger:
    _boolean_result = True

    def log_compare_result(self, key, expected_value, actual_value):
        if expected_value == actual_value:
            ReportLogger.info(f"{key} matches with expected value: {expected_value}")
        else:
            ReportLogger.error(
                f"{key} unmatch, the expected value is {expected_value}, actually value is {actual_value}")
            self._boolean_result = False

    def log_key_exist(self, data, key):
        if key in data:
            ReportLogger.info(f"{key} exists")
        else:
            ReportLogger.error(f"{key} does not exist")
            self._boolean_result = False

    def log_key_value_exist(self, data, key, parent_key):
        if key in data:
            if data[key] is not None:
                ReportLogger.info(f"{parent_key}{key} exists and the value is {data[key]}")
            else:
                ReportLogger.info(f"{parent_key}{key}  exists, but value is None")
                self._boolean_result = False
        else:
            ReportLogger.error(f"{parent_key}{key}  does not exist")
            self._boolean_result = False

    def get_match_result(self):
        return self._boolean_result