import collections
import logging
import time
from datetime import timedelta
from functools import wraps

from .config_utils import ConfigUtils

METRICS_START_TIME = time.time()
Metrics = collections.namedtuple("Metrics", "func_name sum_time num_calls min_time max_time avg_time")


def log(message):
    if ConfigUtils.is_interactive_print_enabled():
        logging.info(message)


def record_stats(fn):
    @wraps(fn)
    def with_perf(*args, **kwargs):
        start = time.time()
        ret = fn(*args, **kwargs)
        end = time.time()
        delta = timedelta(seconds=end - start).total_seconds()
        logging.info(f"Time taken - {delta:.3f} seconds")
        return ret

    return with_perf
