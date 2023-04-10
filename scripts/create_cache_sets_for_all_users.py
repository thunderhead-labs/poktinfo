import pandas as pd
from common.db_utils import ConnFactory
from common.orm.repository import PoktDashboardRepository

from cache_service import cache_set_historical
from scripts.utils import create_cache_set_for_ts_user

"""
Run to create cache sets for all our users at date

Usage: python3 create_cache_sets_by_domain.py <domain1>,<domain2>,<domain3>
"""

if __name__ == "__main__":
    with ConnFactory.dashboard_conn() as session:
        user_ids = [user.id for user in PoktDashboardRepository.get_users(session)]

    for user_id in user_ids:
        set_name = f"user_{user_id}_at_{str(pd.Timestamp.utcnow())[:10]}"
        print(f"Creating {set_name} cache set")
        has_added = create_cache_set_for_ts_user(user_id, set_name)
        if has_added:
            cache_set_historical(user_id, set_name)
