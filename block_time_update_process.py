import time

from common.db_utils import ConnFactory
from common.orm.schema.master import BlockTime
from common.pokt_utils import create_block_time_objects
from common.utils import get_last_block_height

FIRST_BLOCK_HEIGHT = 85000


def run_blocktime_subprocess(is_startup: bool = True):
    with ConnFactory.poktinfo_conn() as session:
        last_block_time = session.query(BlockTime).order_by(BlockTime.height.desc()).first()
        last_block_height = last_block_time.height + 1 if last_block_time else FIRST_BLOCK_HEIGHT
    last_height = last_block_height if is_startup else get_last_block_height()
    while True:
        current_height = get_last_block_height()
        if current_height != last_height:
            has_succeeded = create_block_time_objects(from_height=last_height if is_startup else None)
            if has_succeeded:
                last_height = current_height
                if last_height == get_last_block_height():
                    is_startup = False
        time.sleep(60)
