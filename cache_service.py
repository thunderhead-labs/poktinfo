import ast
import typing
from concurrent.futures import ProcessPoolExecutor as Pool, as_completed
from typing import List

import pandas as pd
from common.db_utils import (
    ConnFactory,
)
from common.orm.repository import PoktInfoRepository
from common.orm.schema import (
    CacheSetStateRangeEntry,
    RewardsCacheSet,
    LatencyCacheSet,
    ErrorsCacheSet,
    NodeCountCacheSet,
    LocationCacheSet,
    CacheSet,
    CacheSetNode,
    PoktInfoBase,
    LatencyCache,
    RewardsInfo,
    ErrorsCache,
)
from common.utils import get_last_block_height, POKT_MULTIPLIER, get_param
from sqlalchemy.orm import Session

from definitions import IS_TEST, LOOK_BACK, get_blocks_interval, STUCK_TOLERANCE
from error_grouping import create_msg_groups
from loggers import logger, perf_logger, stuck_logger

CONTINENT_MAP = {
    "North America": "na",
    "Europe": "eu",
    "Asia": "sg",
}


def add_state_range(
    session: Session,
    service: str,
    start_height: int,
    end_height: int,
    has_added: bool,
    cache_set_id: int,
):
    if not has_added:
        logger.error(f"Failed adding {service, start_height, end_height, cache_set_id}")

    status = "success" if has_added else "failed"
    cache_set_state_range = CacheSetStateRangeEntry(
        cache_set_id=cache_set_id,
        service=service,
        start_height=start_height,
        end_height=end_height,
        status=status,
        interval=get_blocks_interval(),
    )
    PoktInfoRepository.upsert(session, cache_set_state_range)


def cache_rewards(
    session: Session, cache_set_id: int, from_height: int, to_height: int
):
    now = pd.Timestamp.now()
    perf_logger.info(f"Caching rewards for {cache_set_id, from_height, to_height}")

    if not PoktInfoRepository.does_height_exist(session, to_height, RewardsInfo):
        logger.info(
            f"Skipping rewards cache for, rewards not synced yet {from_height, to_height}"
        )
        return

    addresses = PoktInfoRepository.get_cache_set_addresses(session, cache_set_id)
    rewards_info = PoktInfoRepository.get_rewards_info(
        session, from_height, to_height, addresses
    )
    rewards_info = [reward.__to_dict__() for reward in rewards_info]
    rewards_df = pd.DataFrame(
        data=rewards_info,
        columns=[
            "height",
            "address",
            "rewards",
            "chain",
            "relays",
            "token_multiplier",
            "percentage",
            "stake_weight",
        ],
    )

    rewards_cache_sets = []
    chain_groups = rewards_df.groupby([rewards_df["chain"]])
    for chain, group in chain_groups:
        rewards_total = group["rewards"].sum()
        relays_total = group["relays"].sum()
        normalized_rewards_total = (
            PoktInfoRepository.get_rewards_total_per15k(
                session, from_height, to_height, addresses, chain=str(chain)
            )
            / POKT_MULTIPLIER
        )
        rewards_total /= POKT_MULTIPLIER
        rewards_cache_sets.append(
            RewardsCacheSet(
                cache_set_id=cache_set_id,
                rewards_total=float(rewards_total),
                normalized_rewards_total=float(normalized_rewards_total),
                relays_total=int(relays_total),
                chain=str(chain),
                start_height=int(from_height),
                end_height=int(to_height),
                interval=int(get_blocks_interval()),
            )
        )

    has_added = PoktInfoRepository.save_many(session, rewards_cache_sets)
    print(
        f"Added rewards: {has_added}, {len(rewards_cache_sets), from_height, to_height, get_blocks_interval()}"
    )
    add_state_range(
        session, "rewards_cache_set", from_height, to_height, has_added, cache_set_id
    )
    perf_logger.info(
        f"Finished caching rewards for "
        f"{cache_set_id, from_height, to_height}, took {pd.Timestamp.now() - now}"
    )


def cache_latency(
    session: Session, cache_set_id: int, from_height: int, to_height: int
):
    now = pd.Timestamp.now()
    perf_logger.info(
        f"Caching latency for {cache_set_id, from_height, to_height, get_blocks_interval()}"
    )

    if not PoktInfoRepository.does_height_exist(
        session,
        to_height,
        LatencyCache,
        is_range=True,
    ):
        logger.info(
            f"Skipping latency cache for, latency not synced yet {from_height, to_height}"
        )
        return

    addresses = PoktInfoRepository.get_cache_set_addresses(session, cache_set_id)
    latency_cache = PoktInfoRepository.get_latency_cache(
        session, from_height, to_height, addresses
    )
    latency_cache = [latency.__to_dict__() for latency in latency_cache]
    latency_df = pd.DataFrame(
        data=latency_cache,
        columns=[
            "address",
            "total_relays",
            "region",
            "start_height",
            "end_height",
            "avg_latency",
            "avg_p90_latency",
            "avg_weighted_latency",
            "chain",
        ],
    )
    region_groups = latency_df.groupby([latency_df["region"]])
    latency_sets = []
    for name, group in region_groups:
        region = str(name)
        chain_groups = group.groupby([group["chain"]])
        for chain, chain_group in chain_groups:
            chain = str(chain)
            total_relays = chain_group["total_relays"].sum()
            if total_relays > 0:
                avg_latency = float(
                    (chain_group["avg_latency"] * chain_group["total_relays"]).sum()
                    / total_relays
                )
                avg_weighted_latency = float(
                    (
                        chain_group["avg_weighted_latency"]
                        * chain_group["total_relays"]
                    ).sum()
                    / total_relays
                )
                avg_p90_latency = float(
                    (chain_group["avg_p90_latency"] * chain_group["total_relays"]).sum()
                    / total_relays
                )
                latency_sets.append(
                    LatencyCacheSet(
                        cache_set_id=cache_set_id,
                        total_relays=int(total_relays),
                        region=region,
                        chain=chain,
                        avg_latency=float(avg_latency),
                        avg_p90_latency=float(avg_p90_latency),
                        avg_weighted_latency=float(avg_weighted_latency),
                        start_height=int(from_height),
                        end_height=int(to_height),
                        interval=int(get_blocks_interval()),
                    )
                )
    has_added = PoktInfoRepository.save_many(session, latency_sets)
    print(f"Added latency: {has_added}, {len(latency_sets), from_height, to_height}")
    add_state_range(
        session,
        "latency_cache_set",
        from_height,
        to_height,
        has_added,
        cache_set_id,
    )
    perf_logger.info(
        f"Finished caching latency for "
        f"{cache_set_id, from_height, to_height}, took {pd.Timestamp.now() - now}"
    )


def cache_errors(session: Session, cache_set_id: int, from_height: int, to_height: int):
    now = pd.Timestamp.now()
    perf_logger.info(
        f"Caching errors for {cache_set_id, from_height, to_height, get_blocks_interval()}"
    )

    if not PoktInfoRepository.does_height_exist(
        session,
        to_height,
        ErrorsCache,
        is_range=True,
    ):
        logger.info(
            f"Skipping errors cache for, errors not synced yet {from_height, to_height}"
        )
        return

    addresses = PoktInfoRepository.get_cache_set_addresses(session, cache_set_id)
    errors_dict = PoktInfoRepository.get_errors_dict(
        session, from_height, to_height, addresses
    )
    if errors_dict:
        error_sets = []
        chain_msg_groups = create_msg_groups(errors_dict)
        for chain in chain_msg_groups:
            for msg in chain_msg_groups[chain]:
                errors_count = chain_msg_groups[chain][msg]
                error_sets.append(
                    ErrorsCacheSet(
                        cache_set_id=cache_set_id,
                        errors_count=int(errors_count),
                        msg=msg,
                        start_height=from_height,
                        end_height=to_height,
                        chain=chain,
                        interval=get_blocks_interval(),
                    )
                )
        has_added = PoktInfoRepository.save_many(session, error_sets)
        print(f"Added errors: {has_added}, {len(error_sets), from_height, to_height}")
        add_state_range(
            session, "errors_cache_set", from_height, to_height, has_added, cache_set_id
        )
        perf_logger.info(
            f"Finished caching errors for "
            f"{cache_set_id, from_height, to_height}, took {pd.Timestamp.now() - now}"
        )
    else:
        perf_logger.info(
            f"Skipped caching errors for "
            f"{cache_set_id, from_height, to_height}, took {pd.Timestamp.now() - now}"
        )


def cache_node_count(
    session: Session, cache_set_id: int, from_height: int, to_height: int
):
    now = pd.Timestamp.now()
    perf_logger.info(
        f"Caching node count for {cache_set_id, from_height, to_height, get_blocks_interval()}"
    )

    node_cache_sets = []
    chains = get_param(from_height, "pocketcore/SupportedBlockchains")
    chains = ast.literal_eval(chains)
    addresses = PoktInfoRepository.get_cache_set_addresses(session, cache_set_id)

    node_count = PoktInfoRepository.get_node_count(
        session, from_height, to_height, addresses
    )
    if node_count is None or node_count < 0:
        node_count = 0
    node_cache_sets.append(
        NodeCountCacheSet(
            cache_set_id=cache_set_id,
            node_count=int(node_count),
            chain=None,
            start_height=from_height,
            end_height=to_height,
            interval=get_blocks_interval(),
        )
    )

    for chain in chains:
        node_count = PoktInfoRepository.get_node_count(
            session, from_height, to_height, addresses, chain=chain
        )
        if node_count > 0:
            node_cache_sets.append(
                NodeCountCacheSet(
                    cache_set_id=cache_set_id,
                    node_count=int(node_count),
                    chain=chain,
                    start_height=from_height,
                    end_height=to_height,
                    interval=get_blocks_interval(),
                )
            )

    has_added = PoktInfoRepository.save_many(session, node_cache_sets)
    add_state_range(
        session, "node_count_cache_set", from_height, to_height, has_added, cache_set_id
    )
    perf_logger.info(
        f"Finished caching node count for "
        f"{cache_set_id, from_height, to_height}, took {pd.Timestamp.now() - now}"
    )


def cache_locations(
    session: Session, cache_set_id: int, from_height: int, to_height: int
):
    now = pd.Timestamp.now()
    perf_logger.info(
        f"Caching locations for {cache_set_id, from_height, to_height, get_blocks_interval()}"
    )

    addresses = PoktInfoRepository.get_cache_set_addresses(session, cache_set_id)
    locations_dict = PoktInfoRepository.get_locations_dict(session, addresses)
    locations_dict = [location.__to_dict__() for location in locations_dict]
    locations_df = pd.DataFrame(
        data=locations_dict,
        columns=[
            "id",
            "address",
            "ip",
            "height",
            "start_height",
            "end_height",
            "city",
            "continent",
            "country",
            "region",
            "lat",
            "lon",
            "isp",
            "org",
            "as_",
            "date_created",
            "ran_from",
        ],
    )
    location_cache_sets = []
    continent_groups = locations_df.groupby([locations_df["continent"]])
    for continent, continent_group in continent_groups:
        country_groups = continent_group.groupby([continent_group["country"]])
        for country, country_group in country_groups:
            city_groups = country_group.groupby([country_group["city"]])
            for city, city_group in city_groups:
                ip_groups = city_group.groupby([city_group["ip"]])
                for ip, ip_group in ip_groups:
                    ran_froms = ip_group["ran_from"].tolist()
                    # Filter out duplicate ips from different locations
                    # (e.g. sg & na = ip & continent = na -> remove sg)
                    for ran_from in ran_froms:
                        continent_id = (
                            CONTINENT_MAP[continent]
                            if continent in CONTINENT_MAP
                            else "na"
                        )
                        if continent_id == ran_from:
                            ip_group = ip_group[ip_group["ran_from"] == ran_from]

                    isp_groups = ip_group.groupby([ip_group["isp"]])
                    for isp, isp_group in isp_groups:
                        node_count = isp_group["address"].count()
                        lat, lon = isp_group["lat"].iloc[0], isp_group["lon"].iloc[0]
                        location_cache_sets.append(
                            LocationCacheSet(
                                cache_set_id=cache_set_id,
                                node_count=int(node_count),
                                continent=str(continent),
                                country=str(country),
                                city=str(city),
                                ip=str(ip),
                                isp=str(isp),
                                lat=str(lat),
                                lon=str(lon),
                                start_height=from_height,
                                end_height=to_height,
                                interval=get_blocks_interval(),
                            )
                        )
    has_added = PoktInfoRepository.save_many(session, location_cache_sets)
    add_state_range(
        session, "location_cache_set", from_height, to_height, has_added, cache_set_id
    )
    perf_logger.info(
        f"Finished caching locations for "
        f"{cache_set_id, from_height, to_height}, took {pd.Timestamp.now() - now}"
    )


def create_cache_set(
    user_id: int,
    set_name: str,
    addresses: List[str],
    is_public: bool = True,
    is_internal: bool = True,
) -> bool:
    height = get_last_block_height()
    with ConnFactory.poktinfo_conn() as session:
        cache_set = CacheSet(
            user_id=user_id,
            set_name=set_name,
            is_public=is_public,
            is_internal=is_internal,
            is_active=True,
        )
        has_added = PoktInfoRepository.save(session, cache_set)

        if has_added:
            cache_set_id = PoktInfoRepository.get_cache_set_by_user_id_set_name(
                session, user_id, set_name
            ).id
            nodes = []
            for address in addresses:
                nodes.append(
                    CacheSetNode(
                        cache_set_id=cache_set_id,
                        address=address,
                        start_height=height,
                        end_height=None,
                    )
                )
            PoktInfoRepository.save_many(session, nodes)
    return has_added


def update_cache_set_addresses(
    cache_set_id: int, addresses: List[str], deprecated_addresses: List[str]
) -> None:
    height = get_last_block_height()
    with ConnFactory.poktinfo_conn() as session:
        PoktInfoRepository.update_cache_set_nodes(
            session, cache_set_id, deprecated_addresses, height=height
        )
        nodes = []
        for address in addresses:
            nodes.append(
                CacheSetNode(
                    cache_set_id=cache_set_id,
                    address=address,
                    start_height=height,
                    end_height=None,
                )
            )
        PoktInfoRepository.save_many(session, nodes)


def create_service_cache(func, cache_set_id: int) -> None:
    last_height = get_last_block_height()
    from_height = last_height - LOOK_BACK
    # Force start_block to be divisible by get_blocks_interval()
    leftover = from_height % get_blocks_interval() if not IS_TEST else 0
    with ConnFactory.poktinfo_conn() as session:
        for height in range(
            from_height - leftover,
            last_height - get_blocks_interval(),
            get_blocks_interval(),
        ):
            func(session, cache_set_id, height, height + get_blocks_interval())


def create_rewards_cache(cache_set_id: int) -> None:
    create_service_cache(cache_rewards, cache_set_id)


def create_errors_cache(cache_set_id: int) -> None:
    create_service_cache(cache_errors, cache_set_id)


def create_latency_cache(cache_set_id: int) -> None:
    create_service_cache(cache_latency, cache_set_id)


def update_rewards_cache(cache_set_id: int):
    logger.debug(f"Updating rewards cache set for {cache_set_id}")
    table_obj = RewardsCacheSet
    last_height = get_last_block_height()
    with ConnFactory.poktinfo_conn() as session:
        last_recorded_height = get_last_recorded_height(
            session, table_obj, cache_set_id, last_height
        )
    problematic_height, i = 0, 0
    while last_recorded_height + get_blocks_interval() <= last_height:
        leftover = last_recorded_height % get_blocks_interval()
        last_recorded_height -= leftover
        with ConnFactory.poktinfo_conn() as session:
            cache_rewards(
                session,
                cache_set_id,
                last_recorded_height,
                last_recorded_height + get_blocks_interval(),
            )
            is_stuck, i, problematic_height, last_recorded_height = handle_height_logic(
                session,
                table_obj,
                cache_set_id,
                last_recorded_height,
                problematic_height,
                i,
            )
        if is_stuck:
            last_recorded_height += get_blocks_interval()
    logger.debug(f"Finished updating rewards cache set for {cache_set_id}")


def update_latency_cache(cache_set_id: int):
    logger.debug(f"Updating latency cache set for {cache_set_id}")
    table_obj = LatencyCacheSet
    last_height = get_last_block_height()
    with ConnFactory.poktinfo_conn() as session:
        last_recorded_height = get_last_recorded_height(
            session, table_obj, cache_set_id, last_height
        )
    problematic_height, i = 0, 0
    while last_recorded_height + get_blocks_interval() <= last_height:
        leftover = last_recorded_height % get_blocks_interval()
        last_recorded_height -= leftover
        with ConnFactory.poktinfo_conn() as session:
            cache_latency(
                session,
                cache_set_id,
                last_recorded_height,
                last_recorded_height + get_blocks_interval(),
            )
            is_stuck, i, problematic_height, last_recorded_height = handle_height_logic(
                session,
                table_obj,
                cache_set_id,
                last_recorded_height,
                problematic_height,
                i,
            )
        if is_stuck:
            last_recorded_height += get_blocks_interval()
    logger.debug(f"Finished updating latency cache set for {cache_set_id}")


def update_errors_cache(cache_set_id: int):
    logger.debug(f"Updating errors cache set for {cache_set_id}")
    table_obj = ErrorsCacheSet
    last_height = get_last_block_height()
    with ConnFactory.poktinfo_conn() as session:
        last_recorded_height = get_last_recorded_height(
            session, table_obj, cache_set_id, last_height
        )
    problematic_height, i = 0, 0
    leftover = last_recorded_height % get_blocks_interval()
    last_recorded_height -= leftover
    while last_recorded_height + get_blocks_interval() <= last_height:
        with ConnFactory.poktinfo_conn() as session:
            cache_errors(
                session,
                cache_set_id,
                last_recorded_height,
                last_recorded_height + get_blocks_interval(),
            )
            is_stuck, i, problematic_height, last_recorded_height = handle_height_logic(
                session,
                table_obj,
                cache_set_id,
                last_recorded_height,
                problematic_height,
                i,
            )
        if is_stuck:
            last_recorded_height += get_blocks_interval()
    logger.debug(f"Finished updating errors cache set for {cache_set_id}")


def update_node_count(cache_set_id: int):
    logger.debug(f"Updating node count cache set for {cache_set_id}")
    table_obj = NodeCountCacheSet
    last_height = get_last_block_height()
    with ConnFactory.poktinfo_conn() as session:
        last_recorded_height = get_last_recorded_height(
            session, table_obj, cache_set_id, last_height
        )
    problematic_height, i = 0, 0
    while last_recorded_height + get_blocks_interval() <= last_height:
        leftover = last_recorded_height % get_blocks_interval()
        last_recorded_height -= leftover
        with ConnFactory.poktinfo_conn() as session:
            cache_node_count(
                session,
                cache_set_id,
                last_recorded_height,
                last_recorded_height + get_blocks_interval(),
            )
            is_stuck, i, problematic_height, last_recorded_height = handle_height_logic(
                session,
                table_obj,
                cache_set_id,
                last_recorded_height,
                problematic_height,
                i,
            )
        if is_stuck:
            last_recorded_height += get_blocks_interval()
    logger.debug(f"Finished updating node count cache set for {cache_set_id}")


def update_location_cache(cache_set_id: int):
    logger.debug(f"Updating location cache set for {cache_set_id}")
    table_obj = LocationCacheSet
    last_height = get_last_block_height()
    with ConnFactory.poktinfo_conn() as session:
        last_recorded_height = get_last_recorded_height(
            session, table_obj, cache_set_id, last_height
        )
    problematic_height, i = 0, 0
    while last_recorded_height + get_blocks_interval() <= last_height:
        with ConnFactory.poktinfo_conn() as session:
            cache_locations(
                session,
                cache_set_id,
                last_recorded_height,
                last_recorded_height + get_blocks_interval(),
            )
            is_stuck, i, problematic_height, last_recorded_height = handle_height_logic(
                session,
                table_obj,
                cache_set_id,
                last_recorded_height,
                problematic_height,
                i,
            )
        if is_stuck:
            last_recorded_height += get_blocks_interval()
    logger.debug(f"Finished updating location cache set for {cache_set_id}")


def update_cache_set(cache_set_id: int):
    logger.info(f"Starting to update {cache_set_id}")

    with Pool(max_workers=5) as tp:
        futures = [
            tp.submit(update_rewards_cache, cache_set_id),
            tp.submit(update_latency_cache, cache_set_id),
            tp.submit(update_errors_cache, cache_set_id),
            tp.submit(update_node_count, cache_set_id),
            tp.submit(update_location_cache, cache_set_id),
        ]

        for future in as_completed(futures):
            future.result()

        logger.info(f"Finished updating {cache_set_id}")


def cache_set_historical(user_id: int, set_name: str) -> None:
    with ConnFactory.poktinfo_conn() as session:
        cache_set_id = PoktInfoRepository.get_cache_set_by_user_id_set_name(
            session, user_id, set_name
        ).id
    run_historical(cache_set_id)
    print("Finished caching historical data")


def run_historical(cache_set_id: int) -> None:
    with Pool() as executor:
        futures = [
            executor.submit(create_rewards_cache, cache_set_id),
            executor.submit(create_latency_cache, cache_set_id),
            executor.submit(create_errors_cache, cache_set_id),
        ]
        for future in as_completed(futures):
            future.result()


def get_last_recorded_height(
    session: Session,
    table_obj: typing.Type[PoktInfoBase],
    cache_set_id: int,
    last_height: int,
) -> int:
    last_recorded_height = PoktInfoRepository.get_last_recorded_service_height(
        session,
        table_obj,
        is_range=True,
        cache_set_id=cache_set_id,
        interval=get_blocks_interval(),
    )
    if last_recorded_height is None:
        leftover = (last_height - LOOK_BACK) % get_blocks_interval()
        last_recorded_height = last_height - LOOK_BACK - leftover
    return last_recorded_height


def get_transition_height(
    session: Session,
    table_obj: typing.Type[PoktInfoBase],
    cache_set_id: int,
    last_recorded_height: int,
) -> int:
    transition_last_recorded_height = (
        PoktInfoRepository.get_last_recorded_service_height(
            session,
            table_obj,
            is_range=True,
            cache_set_id=cache_set_id,
            interval=get_blocks_interval(),
        )
    )
    transition_last_recorded_height = (
        transition_last_recorded_height
        if transition_last_recorded_height
        else last_recorded_height
    )
    return transition_last_recorded_height


def handle_stuck_height(
    cache_set_id: int,
    last_recorded_height: int,
    problematic_height: int,
    i: int,
    table_obj: typing.Type[PoktInfoBase],
):
    i += 1
    if i % STUCK_TOLERANCE == 0:
        problematic_height = last_recorded_height
        last_recorded_height += get_blocks_interval()
        stuck_logger.info(
            f"Stuck in {table_obj.__tablename__} "
            f"for {cache_set_id} at {last_recorded_height}, skipping."
        )
    if i >= 20:
        stuck_logger.info(
            f"Stuck in {table_obj.__tablename__} "
            f"for {cache_set_id} at {last_recorded_height}, breaking."
        )
        return True, i, problematic_height, last_recorded_height
    return False, i, problematic_height, last_recorded_height


def handle_height_logic(
    session: Session,
    table_obj: typing.Type[PoktInfoBase],
    cache_set_id: int,
    last_recorded_height: int,
    problematic_height: int,
    i: int,
):
    is_stuck = False
    transition_last_recorded_height = get_transition_height(
        session, table_obj, cache_set_id, last_recorded_height
    )
    # Check if height is stuck, if it is handle and if stuck for too long, break
    if is_height_stuck(
        last_recorded_height, transition_last_recorded_height, problematic_height
    ):
        is_stuck, i, problematic_height, last_recorded_height = handle_stuck_height(
            cache_set_id, last_recorded_height, problematic_height, i, table_obj
        )
    else:
        last_recorded_height = transition_last_recorded_height
    return is_stuck, i, problematic_height, last_recorded_height


def is_height_stuck(
    last_recorded_height: int,
    transition_last_recorded_height: int,
    problematic_height: int,
) -> bool:
    return (
        last_recorded_height == transition_last_recorded_height
        or problematic_height >= transition_last_recorded_height
    )
