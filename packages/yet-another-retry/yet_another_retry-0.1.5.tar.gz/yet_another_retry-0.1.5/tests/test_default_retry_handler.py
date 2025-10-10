import pytest
from yet_another_retry.retry_handlers import default_retry


def test_default_retry_handler():
    delay_seconds = default_retry(e=Exception, retry_config={})

    assert delay_seconds == 0
