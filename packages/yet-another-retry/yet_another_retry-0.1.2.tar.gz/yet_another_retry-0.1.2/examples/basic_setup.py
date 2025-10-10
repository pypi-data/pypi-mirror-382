from yet_another_retry import retry
import logging


@retry()
def my_function():
    """This function will use the default retry and exception handlers and fail the default nr of times"""

    logging.info("Raising an error")
    raise Exception("Raising an error")
