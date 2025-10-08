"""
This module provides a decorator for logging the execution time of functions.
"""

import logging
import time


def log(func):
    """
    Log the execution time of the main processing function
    """

    def wrap_log(*args, **kwargs):
        logger = logging.getLogger(func.__name__)
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        logger.info("Execution time: %.4f seconds", duration)
        return result

    return wrap_log
