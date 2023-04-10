import argparse

from cache_service import (
    create_cache_set,
    cache_set_historical,
)
from scripts.utils import create_cache_set_for_ts_user

"""
CLI to create basic cache sets

Usage:
python3 cache_service_cli.py --createset user_id --setname set_name --addresses address1,address2,address3
python3 cache_service_cli.py --createset user_id --setname set_name
"""

parser = argparse.ArgumentParser(description="Process some integers.")

parser.add_argument(
    "--createset", type=str, nargs="+", default="", help="create cache set for user_id"
)
parser.add_argument(
    "--addresses", type=str, nargs="+", default="", help="add to cache set addresses"
)
parser.add_argument(
    "--setname", type=str, nargs="+", default="", help="the cache set name"
)
parser.add_argument("--public", type=str, nargs="+", default="", help="is set public")
parser.add_argument(
    "--internal", type=str, nargs="+", default="", help="is set internal"
)

args = parser.parse_args()

if __name__ == "__main__":
    if args.createset:
        user_id = int(args.createset[0])
        set_name = args.setname[0]
        is_public = eval(args.public[0])
        is_internal = eval(args.internal[0])
        print(
            user_id, set_name, is_public, is_internal, args.public[0], args.internal[0]
        )
        if args.addresses:
            print("with addresses")
            # python3 cache_service_cli.py --createset user_id --setname set_name --public is_public --internal is_internal --addresses address1,address2,address3
            addresses = [address for address in args.addresses[0].split(",")]
            print(addresses)
            create_cache_set(
                user_id,
                set_name,
                addresses,
                is_public=is_public,
                is_internal=is_internal,
            )
        else:
            print("With user")
            # python3 cache_service_cli.py --createset user_id --setname set_name --public is_public --internal is_internal
            create_cache_set_for_ts_user(
                user_id, set_name, is_public=is_public, is_internal=is_internal
            )
        cache_set_historical(user_id, set_name)
