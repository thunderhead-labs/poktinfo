import sys
from concurrent.futures import ProcessPoolExecutor as Pool, as_completed
from multiprocessing import Process
from time import sleep

from common.db_utils import ConnFactory
from common.orm.repository import PoktInfoRepository
from common.price_utils import record_pocket_price
from common.utils import get_last_block_height

from block_time_update_process import run_blocktime_subprocess
from definitions import IS_TEST, set_blocks_interval, get_blocks_interval

if len(sys.argv) > 1:
    set_blocks_interval(int(sys.argv[1]))
if len(sys.argv) > 2:
    mode = str(sys.argv[1])
else:
    mode = None

from cache_service import (
    update_cache_set,
    update_rewards_cache,
    update_errors_cache,
    update_latency_cache,
)
from loggers import logger

if __name__ == "__main__":
    coin, currency = "pokt", "usd"
    last_recorded_height = get_last_block_height() - get_blocks_interval()

    p = Process(target=run_blocktime_subprocess)
    p.start()

    while True:
        try:
            last_height = get_last_block_height()
            # Force start_block to be divisible by BLOCKS_INTERVAL
            leftover = last_height % get_blocks_interval()
            if IS_TEST or leftover < 3:

                try:
                    # Record pocket price
                    record_pocket_price(coin, currency, last_height)
                except Exception as e:
                    logger.error(
                        f"Failed recording price for {coin} at {last_height}, {e}"
                    )

                logger.info(
                    f"Updating for {last_height}, Blocks interval - {get_blocks_interval()}"
                )
                if last_recorded_height + get_blocks_interval() <= last_height:
                    with ConnFactory.poktinfo_conn() as session:
                        cache_sets = PoktInfoRepository.get_cache_sets(session)
                        cache_set_ids = [cache_set.id for cache_set in cache_sets]

                    futures = []
                    with Pool(max_workers=8) as tp:
                        for cache_set_id in cache_set_ids:
                            func = update_cache_set
                            if mode == "rewards":
                                func = update_rewards_cache
                            elif mode == "errors":
                                func = update_errors_cache
                            elif mode == "latency":
                                func = update_latency_cache
                            futures.append(tp.submit(func, cache_set_id))

                        for future in as_completed(futures):
                            future.result()

                    last_recorded_height = last_height
                    sleep(60 * 15 if mode != "fast" else 1)
        except Exception as e:
            logger.error(e)

        sleep(60 if mode is None else 1)
