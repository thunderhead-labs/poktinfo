import os

from common.loggers import get_logger

from definitions import get_blocks_interval

path = os.path.dirname(os.path.realpath(__file__))
service_name = "poktinfo"
logger = get_logger(path, service_name, f"{service_name}_{get_blocks_interval()}")
perf_logger = get_logger(
    path, service_name, f"poktinfo_profiler_{get_blocks_interval()}"
)
stuck_logger = get_logger(path, service_name, f"poktinfo_stuck_{get_blocks_interval()}")
