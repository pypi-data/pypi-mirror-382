"""Functions for logging."""

import datetime
import logging
from io import StringIO
import functools


def init_log(version=None):
    """Enable logging."""
    start_time = "{:%Y-%b-%d %H:%M:%S}".format(datetime.datetime.now())
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    log_stream = StringIO()
    log_handler = logging.StreamHandler(log_stream)
    log_handler.setLevel(logging.INFO)
    logger.addHandler(log_handler)
    logger.propagate = False
    # start log
    if version:
        logger.info("version " + f"{version}")
    logger.info(f"{start_time}\n")
    return logger, log_stream


def log(func):
    """To decorate functions whose output should be logged."""

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        res = func(self, *args, **kwargs)
        # store call to function in log_string
        method_name = func.__name__
        log_string = method_name + "("
        if any(args):
            args_list = [repr(a) for a in args]
        else:
            args_list = []
        if any(kwargs):
            kwargs_list = [f"{k}={v!r}" for k, v in kwargs.items()]
        else:
            kwargs_list = []
        log_string += ", ".join(args_list + kwargs_list) + ")\n"
        self.logger.info(log_string)
        return res

    return wrapper
