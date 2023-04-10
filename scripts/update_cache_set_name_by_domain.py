import sys

from common.utils import get_last_block_height

sys.path.insert(0, "C:/Users/user/Documents/TS/poktinfo")
from common.db_utils import ConnFactory
from common.orm.repository import PoktInfoRepository

from cache_service import update_cache_set_addresses, update_cache_set

"""
Run to create cache sets for all nodes that contain domain at date

Usage: python3 update_cache_set_name_by_domain.py <domain_old> <domain_new>
"""

if __name__ == "__main__":
    if len(sys.argv) > 1:
        domain_old = str(sys.argv[1])
        domain_new = str(sys.argv[2])

        height = get_last_block_height()
        with ConnFactory.poktinfo_conn() as session:
            addresses = PoktInfoRepository.get_addresses_by_domain(session, domain_new)
            print(len(addresses))

            # set_name = f"{domain}_at_{str(pd.Timestamp.utcnow())[:10]}"
            set_name = domain_new
            print(f"Updating {set_name} cache set")
            cache_set_id = PoktInfoRepository.get_cache_set_by_user_id_set_name(
                session, 0, domain_old
            ).id
            old_addresses = PoktInfoRepository.get_cache_set_addresses(
                session, cache_set_id, height
            )
            deprecated_addresses = list(set(addresses) ^ set(old_addresses))
            PoktInfoRepository.rename_cache_set(session, cache_set_id, set_name)
            print("Renamed cache set, updating addresses")
            update_cache_set_addresses(cache_set_id, addresses, deprecated_addresses)
            update_cache_set(cache_set_id)
