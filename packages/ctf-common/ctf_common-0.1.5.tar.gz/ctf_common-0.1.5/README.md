## Environment Requirements

- Python 3.7 and higher
- pip

## update report API host name
- default value of API host is : http://127.0.0.1:8000/api
- To update the API host to other path, update the environment parameter
os.setenv("CTF_REPORT_HOST", "http://your.api.host/api")

## Use in automation project
### Create run/case/steps in automation environment 
- import "report_manager"
```
from ctf_common.reports.report_manager import ReportManager
```

- before all features:
```
ReportManager.create_test_run(scope_name="Debug",tags=tags_string)
context.run_result = run_result
```
- after all features:
```
 ReportManager.complete_test_run(context.run_result)
```
- before scenario
```
ReportManager.create_test_case(context.run_result.id,scenario.name, feature=context.feature_name)
 context.case_result = case_result
```

- after scenario
```
 ReportManager.complete_test_case(context.case_result)
 ```

- before step
```
 step_result = ReportManager.create_test_step(context.case_result.id, step.name)
 context.step_result = step_result
```
- after step
```
 ReportManager.complete_test_step(context.step_result)
```

### add logs for test steps
- import "report_logger"
 ```
from ctf_common.reports.report_logger import ReportLogger
 ```

- add logs with defined log level
```
-  ReportLogger.info("test step log information")
-  ReportLogger.error("test step failed with error message")
-  ReportLogger.warn("test step warning message")
-  ReportLogger.success("step passed with green color highlights on screen")
```