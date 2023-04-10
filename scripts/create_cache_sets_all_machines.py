import pandas as pd
from common.db_utils import ConnFactory, fetch_all_dict, fetch_all_raw

from cache_service import cache_set_historical, create_cache_set

"""
Run to create cache sets for all machines in infra db
"""

if __name__ == "__main__":
    is_public = True
    is_internal = True

    ConnFactory.use_psycopg2()
    with ConnFactory.infradb_conn() as conn:
        select_stmt = f"""SELECT m.public_ip as MACHINE_IP, s.NUMBER as NODE_NUMBER
                    FROM servicers as s

                    INNER JOIN containers as c
                    ON s.CONTAINER_ID=c.ID

                    INNER JOIN machines as m
                    ON c.MACHINE_ID=m.PUBLIC_IP

                    WHERE c.purpose LIKE 'POKT%' AND c.STATUS = 'PROVISIONED'"""
        machines_data = fetch_all_raw(conn, select_stmt)
    machines_df = pd.DataFrame(machines_data, columns=["ip", "node"])

    machine_nodes = {}
    for ip in machines_df["ip"].unique():
        machine_nodes[ip] = list(
            machines_df.loc[machines_df["ip"] == ip]["node"].values
        )

    with ConnFactory.dashboard_conn() as conn:
        select_stmt = f"""SELECT subdomain, address FROM public.main_node"""
        node_address_map = fetch_all_dict(conn, select_stmt)

    machine_addresses = {}
    for ip in machine_nodes:
        nodes = machine_nodes[ip]
        for node in nodes:
            if f"node{node}" in node_address_map:
                address = node_address_map[f"node{node}"]
                if ip in machine_addresses:
                    machine_addresses[ip].append(address)
                else:
                    machine_addresses[ip] = [address]

    ConnFactory.use_sqlalchemy()
    for ip in machine_addresses:
        set_name = f"machine_{ip}_at_{str(pd.Timestamp.utcnow())[:10]}"
        print(f"Creating {set_name} cache set")
        addresses = machine_addresses[ip]
        has_added = create_cache_set(
            0, set_name, addresses, is_public=is_public, is_internal=is_internal
        )
        if has_added:
            cache_set_historical(0, set_name)
