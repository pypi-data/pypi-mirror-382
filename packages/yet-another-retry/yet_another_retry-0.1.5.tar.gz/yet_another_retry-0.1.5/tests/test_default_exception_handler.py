import pytest
from yet_another_retry.exception_handlers import default_exception


def test_default_retry_handler():
    try:
        default_exception(e=Exception, retry_config={})
        assert False
    except Exception:
        assert True
