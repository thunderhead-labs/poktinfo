IS_TEST = False
LOOK_BACK = 1000
BLOCKS_INTERVAL = 4
STUCK_TOLERANCE = 1


def set_blocks_interval(interval: int) -> None:
    global BLOCKS_INTERVAL
    BLOCKS_INTERVAL = interval


def get_blocks_interval() -> int:
    return BLOCKS_INTERVAL
