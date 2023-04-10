import sys

from common.price_utils import record_historical_pocket_prices

"""
Run to save historical coin prices to the database

Usage: python3 save_historical_coin_prices.py <start_date> <end_date>
"""

# TODO get kwargs, and include coin, currency
coin, currency = "pokt", "usd"
from_date, to_date = "2022-01-01", "2022-10-20"

if len(sys.argv) > 2:
    from_date = str(sys.argv[1])
    to_date = str(sys.argv[2])

record_historical_pocket_prices(coin, currency, from_date, to_date)
