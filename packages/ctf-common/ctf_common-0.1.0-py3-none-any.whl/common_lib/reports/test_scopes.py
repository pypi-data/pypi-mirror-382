from enum import Enum

class TestScope(Enum):
    REGRESSION_TEST = 'Regression Test'
    SMOKE_TEST = 'Smoke Test'
    INTEGRATION_TEST = 'Integration Test'
    SECURITY_TEST = 'Security Test'
    PERFORMANCE_TEST = 'Performance Test'
    API_TEST = 'API Test'
    UI_TEST = 'UI Test'
    END_TO_END_TEST = 'End-to-End Test'
    PROD_CHECKOUT = 'Prod Checkout'

    @classmethod
    def get_all_scopes(cls):
        return [scope.value for scope in cls]

    @classmethod
    def is_valid_scope(cls, scope_name):
        return scope_name in cls.get_all_scopes()