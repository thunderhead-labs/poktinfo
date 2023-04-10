from common.db_utils import ConnFactory
from common.orm.repository import PoktDashboardRepository

from cache_service import create_cache_set


def create_cache_set_for_ts_user(
    user_id: int, set_name: str, is_public: bool = True, is_internal: bool = True
) -> bool:
    with ConnFactory.dashboard_conn() as session:
        addresses = PoktDashboardRepository.get_addresses_of_nodes(session, user_id)
    return create_cache_set(
        user_id, set_name, addresses, is_public=is_public, is_internal=is_internal
    )
