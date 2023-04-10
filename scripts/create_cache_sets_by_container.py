import pandas as pd
from common.db_utils import ConnFactory, fetch_all_dict, fetch_all_raw

from cache_service import cache_set_historical, create_cache_set

"""
Run to create cache sets for all containers in infra db
"""

if __name__ == "__main__":
    is_public = True
    is_internal = True

    ConnFactory.use_psycopg2()
    with ConnFactory.infradb_conn() as conn:
        select_stmt = f"""SELECT c.ID as CONTAINER_ID, s.NUMBER as NODE_NUMBER
                    FROM servicers as s

                    INNER JOIN containers as c
                    ON s.CONTAINER_ID=c.ID

                    INNER JOIN machines as m
                    ON c.MACHINE_ID=m.PUBLIC_IP"""
        machines_data = fetch_all_raw(conn, select_stmt)
    machines_df = pd.DataFrame(machines_data, columns=["container_id", "node"])

    machine_nodes = {}
    for container_id in machines_df["container_id"].unique():
        machine_nodes[container_id] = list(
            machines_df.loc[machines_df["container_id"] == container_id]["node"].values
        )

    with ConnFactory.dashboard_conn() as conn:
        select_stmt = f"""SELECT subdomain, address FROM public.main_node"""
        node_address_map = fetch_all_dict(conn, select_stmt)

    machine_addresses = {}
    for container_id in machine_nodes:
        nodes = machine_nodes[container_id]
        for node in nodes:
            if f"node{node}" in node_address_map:
                address = node_address_map[f"node{node}"]
                if container_id in machine_addresses:
                    machine_addresses[container_id].append(address)
                else:
                    machine_addresses[container_id] = [address]

    ConnFactory.use_sqlalchemy()
    for container_id in machine_addresses:
        set_name = f"container_{container_id}_at_{str(pd.Timestamp.utcnow())[:10]}"
        print(f"Creating {set_name} cache set")
        addresses = machine_addresses[container_id]
        has_added = create_cache_set(
            0, set_name, addresses, is_public=is_public, is_internal=is_internal
        )
        if has_added:
            cache_set_historical(0, set_name)
