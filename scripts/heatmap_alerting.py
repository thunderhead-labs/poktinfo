import sys
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
from common.db_utils import ConnFactory
from common.orm.repository import PoktInfoRepository
from common.utils import get_last_block_height, POKT_MULTIPLIER
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

"""
usage: python3 heatmap_alerting.py <set_names> <chains> <interval> <query_type> <channel>

This script will generate a heatmap of the question for the given sets and chains, for the given interval.

Based on interval start/end height are calculated from current height.
Then based on the question get_heatmap_data is called with the relevant function.
Then the heatmap is saved to a png file and sent to the given slack channel.

To add a new question, you can use get_heatmap_data() that gets a function
that returns a value from db between heights and for a list of addresses.
Chain is preferred as well but not required.
"""


SLACK_BOT_TOKEN = "your-token"


def get_heatmap_data(func, sets, chains, from_height, to_height):
    """
    Template function for getting 2d data from poktinfo db using func
    Value from func is always divided by node count and func should be filterable by chain as one of its params
    """
    with ConnFactory.poktinfo_conn() as session:
        data = defaultdict(dict)
        for set_name in sets:
            try:
                cache_set_id = PoktInfoRepository.get_cache_set_by_user_id_set_name(
                    session, 0, set_name
                ).id
            except:
                print(f"Set {set_name} not found")
                continue
            addresses = PoktInfoRepository.get_cache_set_addresses(
                session, cache_set_id
            )
            for chain_name in chains:
                if "all" in chain_name.lower():
                    chain = None
                else:
                    chain = chain_name
                value = func(session, from_height, to_height, addresses, chain=chain)
                if not value:
                    value = -1
                node_count = PoktInfoRepository.get_node_count(
                    session, from_height, to_height, addresses, chain=chain
                )
                if set_name == "pokt network":
                    set_name = "network avg"
                print(set_name, chain_name, value, node_count)
                data[set_name][chain_name] = (
                    value / node_count if node_count and node_count > 0 else -1
                )
                print(
                    (value / node_count if node_count and node_count > 0 else -1)
                    / POKT_MULTIPLIER
                )
    x_axis = list(data.keys())
    y_axis = list(data[x_axis[0]].keys())

    # calculate average values for each chain across all sets
    chain_averages = {}
    for chain_name in y_axis:
        total = 0
        count = 0
        for set_name in x_axis:
            total += data[set_name][chain_name]
            count += 1
        if count > 0:
            chain_averages[chain_name] = total / count
        else:
            chain_averages[chain_name] = -1

    # sort chains (y_axis) by average value
    y_axis = sorted(y_axis, key=lambda x: chain_averages[x], reverse=True)

    # sort set_name (x_axis) by the values of the first chain
    x_axis = sorted(x_axis, key=lambda x: data[x][y_axis[0]], reverse=True)

    return np.array([[data[x][y] for y in y_axis] for x in x_axis]), x_axis, y_axis


def get_rewards_heatmap_data(sets, chains, from_height, to_height):
    data, set_names, chains = get_heatmap_data(
        PoktInfoRepository.get_rewards_total_per15k,
        sets,
        chains,
        from_height,
        to_height,
    )
    return np.around(data / POKT_MULTIPLIER, 2), set_names, chains


def get_relays_heatmap_data(sets, chains, from_height, to_height):
    data, set_names, chains = get_heatmap_data(
        PoktInfoRepository.get_relays_total, sets, chains, from_height, to_height
    )
    return np.around(data / 1000, 1), set_names, chains


def save_heatmap_png(
    data, set_names, chains, title, from_height, to_height, factor=1
) -> str:
    fig, ax = plt.subplots()

    # normalizing each column to be between 0 and 1. This makes the heatmap calculation to be by column rather
    # than through the whole chart, which would make all the small chains be always red, even if they are outperforming NA.
    x_normed = data / data.max(axis=0)

    # plotting the normalized heatmap
    ax.imshow(x_normed, cmap="RdYlGn")

    # Show all ticks and label them with the respective list entries
    ax.set_xticks(np.arange(len(chains)), labels=chains)
    ax.set_yticks(np.arange(len(set_names)), labels=set_names)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    for i in range(len(set_names)):
        for j in range(len(chains)):
            # labelling the plot with the original numbers (not the normalized ones)
            text = ax.text(j, i, data[i, j], ha="center", va="center", color="black")

    ax.set_title(title)
    fig.tight_layout()
    plt.show()
    fig.set_size_inches(round(20 * factor), round(10 * factor))
    plt.savefig(f"{title}_{from_height}_{to_height}.png")
    return f"{title}_{from_height}_{to_height}.png"


def send_to_slack_channel(file_path: str, channel: str):
    client = WebClient(token=SLACK_BOT_TOKEN)
    try:
        with open(file_path, "rb") as image:
            response = client.files_upload(channels=channel, file=image)
    except SlackApiError as e:
        print("Error sending message: {}".format(e))


if len(sys.argv) > 5:
    set_names = str(sys.argv[1]).split(",")
    chains = str(sys.argv[2]).split(",")
    interval = int(sys.argv[3])
    question = str(sys.argv[4])
    channel = str(sys.argv[5])

    print(
        f"set_names: {set_names}, chains: {chains}, interval: {interval}, question: {question}, channel: {channel}"
    )

    height = get_last_block_height()
    to_height = height  # - height % interval
    from_height = to_height - interval

    if question == "rewards":
        data, set_names, chains = get_rewards_heatmap_data(
            set_names, chains, from_height, to_height
        )
        title = f"Average reward normalized by stake weight per node for domain and chain {from_height} - {to_height}"
        factor = 1
    elif question == "relays":
        data, set_names, chains = get_relays_heatmap_data(
            set_names, chains, from_height, to_height
        )
        title = f"Average relays per node div by 1000 for domain and chain {from_height} - {to_height}"
        factor = 1
    else:
        data, title, factor = None, None, None

    if len(data):
        path = save_heatmap_png(
            data, set_names, chains, title, from_height, to_height, factor
        )
        send_to_slack_channel(path, channel)
