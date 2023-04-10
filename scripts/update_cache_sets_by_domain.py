import sys
import pandas as pd

sys.path.insert(0, "/home/debian/poktinfo")

from common.utils import get_last_block_height
from common.db_utils import ConnFactory
from common.orm.repository import PoktInfoRepository

from loggers import logger
from cache_service import update_cache_set, update_cache_set_addresses

"""
Run to create cache sets for all nodes that contain domain at date

Usage: python3 update_cache_sets_by_domain.py <domain1>,<domain2>,<domain3>
"""

if __name__ == "__main__":
    domains = [
        "c0d3r.org",
        "nodefleet.org",
        "thunderstake.org",
        "poktnodes.network",
        "nodies.org",
        "poktscan.cloud",
        "liquify.ltd",
        "easy2stake.com",
        "node-river-001.com",
        "sendnodes.io",
        "blokhub.org",
        "blockspaces.global",
        "zp-labs.net",
        "nachoracks.com",
        "poktschool.com",
    ]

    logger.debug("2")

    if len(sys.argv) > 1:
        domains = str(sys.argv[1]).split(",")

    height = get_last_block_height()
    logger.info(f"Updating cache sets of domains: {domains}")
    with open("cron.text", "w") as f:
        f.write(f"{pd.Timestamp.utcnow()} Updating cache sets of domains: {domains}\n")
        try:
            with ConnFactory.poktinfo_conn() as session:
                for domain in domains:
                    addresses = PoktInfoRepository.get_addresses_by_domain(
                        session, domain
                    )
                    f.write(str(len(addresses)))
                    # set_name = f"{domain}_at_{str(pd.Timestamp.utcnow())[:10]}"
                    set_name = domain
                    logger.debug(f"Updating {set_name} cache set")
                    f.write(f"Updating {set_name} cache set\n")
                    cache_set_id = PoktInfoRepository.get_cache_set_by_user_id_set_name(
                        session, 0, set_name
                    ).id
                    old_addresses = PoktInfoRepository.get_cache_set_addresses(
                        session, cache_set_id, height
                    )
                    deprecated_addresses = list(set(addresses) ^ set(old_addresses))
                    update_cache_set_addresses(
                        cache_set_id, addresses, deprecated_addresses
                    )
                    update_cache_set(cache_set_id)
            f.write(
                f"{pd.Timestamp.utcnow()} Finished updating cache sets of domains: {domains}\n"
            )
        except Exception as e:
            with open("error.txt", "w") as f2:
                f2.write("yea..")
                f2.write(f"Error: {e}")
