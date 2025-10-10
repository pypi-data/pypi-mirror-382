from typing import Callable
import time
import inspect
from yet_another_retry.retry_handlers import default_retry
from yet_another_retry.exception_handlers import default_exception


def retry(
    retry_exceptions: Exception | tuple[Exception] = (Exception),
    fail_on_exceptions: Exception | tuple[Exception] = (),
    tries: int = 3,
    retry_callable: Callable = default_retry,
    error_callable: Callable = default_exception,
    extra_kwargs: dict = {},
) -> Callable:
    """Decorator for retrying a function

    If the decorated function contains parameter named "retry_config" the decorator will pass the following dict as a parameter to the function:

    ```python
        retry_config = {
            "retry_exceptions": retry_exceptions,
            "fail_on_exceptions": fail_on_exception,
            "tries": tries,
            "op_kwargs": op_kwargs,
            "retry_callable": retry_callable,
            "error_callable": error_callable,
            "extra_kwargs": extra_kwargs,
            "attempt": 1    # which attempt number currently running
        }

    ```

    Args:
        retry_exceptions(tuple[Exception]): An Exception or tuple of exceptions to retry. All other exceptions will fail. Defaults to (Exception) meaning all exceptions are retried unless this value is modified.
        fail_on_exceptions(tuple[Exception]): An Exception or tuple of exception to not retry but instead raise error if it occures. Defaults to ()
        tries(int): Maximum number of retries to attempt. Defaults to 3
        retry_callable(Callable): Callable function to run in case of retries. Defaults to base retry_delay_seconds function
        error_callable(Callable): Callable function to run in case of erroring out, either by reaching max retries +1 or hitting a fail_on_exception exception. Defaults to base raise_exception function.
        extra_kwargs(dict): A dict of extra parameters to pass to the handlers.
                            If supplied will be passed to the handler as normal parameters as well as in the retry_config as "extra_kwargs".
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            retry_config = {
                "retry_exceptions": retry_exceptions,
                "fail_on_exceptions": fail_on_exceptions,
                "tries": tries,
                "retry_callable": retry_callable,
                "error_callable": error_callable,
                "extra_kwargs": extra_kwargs,
                "attempt": 0,
            }
            # parameters from the decorated function
            # used to check if the decorated function has a "retry_config" parameter
            send_config = (
                True if "retry_config" in inspect.signature(func).parameters else False
            )

            for i in range(1, tries + 1):
                try:
                    if send_config:
                        kwargs["retry_config"] = retry_config
                        kwargs["retry_config"]["attempt"] = i
                    return func(*args, **kwargs)

                except fail_on_exceptions as e:
                    if error_callable:
                        error_callable(e, retry_config=retry_config, **extra_kwargs)
                    # if the error callable did not raise the error we raise it here
                    raise e

                except retry_exceptions as e:
                    if i == tries:
                        if error_callable:
                            error_callable(e, retry_config=retry_config, **extra_kwargs)
                        # if the error callable did not raise the error we raise it here
                        raise e
                    delay_seconds = retry_callable(
                        e, retry_config=retry_config, **extra_kwargs
                    )

                    # the return from the callable must be an int or a float
                    if not isinstance(delay_seconds, (int, float)):
                        raise TypeError(
                            f"The retry_callable did not return an int or float. Can not use {type(delay_seconds)} as input to sleep"
                        )
                    time.sleep(delay_seconds)

        return wrapper

    return decorator
