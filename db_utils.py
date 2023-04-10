from common.db_utils import fetch_all, execute_stmt, fetch_one


def add_cache_set_entry(conn, user_id: int, set_name: str):
    select_stmt = f"""SELECT set_name FROM public.cache_set
WHERE user_id={user_id}"""
    if set_name not in fetch_all(conn, select_stmt):
        insert_stmt = f"""INSERT INTO public.cache_set(user_id, set_name)
VALUES ({user_id}, '{set_name}')"""
        return execute_stmt(conn, insert_stmt)
    return False


def add_cache_set_node_entry(conn, cache_set_id: int, address: str):
    insert_stmt = f"""INSERT INTO public.cache_set_node(cache_set_id, address)
VALUES ({cache_set_id}, '{address}')"""
    return execute_stmt(conn, insert_stmt)


def add_rewards_cache_set_entry(
    conn, cache_set_id: int, rewards_total: float, from_height: int, to_height: int
):
    insert_stmt = f"""INSERT INTO public.rewards_cache_set(cache_set_id, rewards_total,
start_height, end_height)
VALUES ({cache_set_id}, {rewards_total}, {from_height}, {to_height})"""
    return execute_stmt(conn, insert_stmt)


def add_latency_cache_set_entry(
    conn,
    cache_set_id: int,
    total_relays: float,
    region: str,
    from_height: int,
    to_height: int,
    avg_latency: float,
    avg_p90_latency: float,
    avg_weighted_latency: float,
    chain: str,
):
    insert_stmt = f"""INSERT INTO public.latency_cache_set(cache_set_id, total_relays,
region, start_height, end_height, avg_latency, avg_p90_latency, avg_weighted_latency, chain)
VALUES ({cache_set_id}, {total_relays}, '{region}', {from_height}, {to_height},
{avg_latency}, {avg_p90_latency}, {avg_weighted_latency}, '{chain}')"""
    return execute_stmt(conn, insert_stmt)


def add_location_cache_set_entry(
    conn,
    cache_set_id: int,
    node_count: int,
    region: str,
    from_height: int,
    to_height: int,
):
    insert_stmt = f"""INSERT INTO public.location_cache_set(cache_set_id, node_count,
    region, start_height, end_height)
    VALUES ({cache_set_id}, {node_count}, '{region}', {from_height}, {to_height})"""
    return execute_stmt(conn, insert_stmt)


def add_errors_cache_set_entry(
    conn,
    cache_set_id: int,
    errors_count: int,
    msg: str,
    from_height: int,
    to_height: int,
    chain: str,
):
    insert_stmt = f"""INSERT INTO public.errors_cache_set(cache_set_id, errors_count,
msg, start_height, end_height, chain)
VALUES ({cache_set_id}, {errors_count}, '{msg}', {from_height}, {to_height}, '{chain}')"""
    return execute_stmt(conn, insert_stmt)


def add_node_count_cache_set_entry(
    conn, cache_set_id: int, node_count: int, from_height: int, to_height: int
):
    insert_stmt = f"""INSERT INTO public.node_count_cache_set(cache_set_id, node_count,
start_height, end_height)
VALUES ({cache_set_id}, {node_count}, {from_height}, {to_height})"""
    return execute_stmt(conn, insert_stmt)


def get_cache_set_id(conn, user_id: int, set_name: str):
    select_stmt = f"""SELECT id FROM public.cache_set
WHERE user_id={user_id} AND set_name='{set_name}'"""
    return fetch_one(conn, select_stmt)


def get_all_cache_set_ids(conn):
    select_stmt = """SELECT id FROM public.cache_set"""
    return fetch_all(conn, select_stmt)


def get_cache_set_addresses(conn, cache_set_id: int):
    select_stmt = f"""SELECT address FROM public.cache_set_node
WHERE cache_set_id={cache_set_id}"""
    return fetch_all(conn, select_stmt)


def get_last_recorded_cached_height(conn, service_name: str, cache_set_id: int):
    select_stmt = f"""SELECT MAX(end_height) FROM public.cache_set_state_range_entry
WHERE service='{service_name}' AND cache_set_id={cache_set_id} AND status='success'"""
    return fetch_one(conn, select_stmt)


def get_current_state(conn, service_name: str):
    select_stmt = f"""SELECT MAX(height) FROM public.services_state
WHERE service='{service_name}'"""
    return fetch_one(conn, select_stmt)


def get_current_range_state(conn, service_name: str):
    select_stmt = f"""SELECT MAX(end_height) FROM public.services_state_range
WHERE service='{service_name}'"""
    return fetch_one(conn, select_stmt)
