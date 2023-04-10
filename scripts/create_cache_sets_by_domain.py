import sys

sys.path.insert(0, "C:/Users/user/Documents/TS/poktinfo")

from common.db_utils import ConnFactory
from common.orm.repository import PoktInfoRepository

from cache_service import create_cache_set, cache_set_historical

"""
Run to create cache sets for all nodes that contain domain at date

Usage: python3 create_cache_sets_by_domain.py <domain1>,<domain2>,<domain3>
"""

if __name__ == "__main__":
    domains = [
        "pokt network",
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
        "cryptonode.tools",
        "aapokt.com",
        "spacebelt.cloud",
        "nodifi.io",
    ]

    if len(sys.argv) > 1:
        domains = str(sys.argv[1]).split(",")
    if len(sys.argv) > 3:
        is_public = bool(sys.argv[2])
        is_internal = bool(sys.argv[3])
    else:
        is_public = True
        is_internal = True

    set_names = []
    with ConnFactory.poktinfo_conn() as session:
        for domain in domains:
            addresses = PoktInfoRepository.get_addresses_by_domain(session, domain)
            print(len(addresses))

            # set_name = f"{domain}_at_{str(pd.Timestamp.utcnow())[:10]}"
            set_name = domain
            print(f"Creating {set_name} cache set")
            has_added = create_cache_set(
                0, set_name, addresses, is_public=is_public, is_internal=is_internal
            )
            if has_added:
                print(f"Created {set_name} cache set, caching historical data")
                cache_set_historical(0, set_name)
