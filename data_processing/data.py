import pandas as pd
import requests
import json
import time
from datetime import datetime, timedelta
from dateutil import tz

def load_data():
    ftx_recovery_model_xlsx = pd.read_excel('FTX Public Overview.xlsx', sheet_name=None, header=0, index_col=0)

    # Read Excel sheets into DataFrames
    cash_df = ftx_recovery_model_xlsx['Cash']
    assets_df = ftx_recovery_model_xlsx['Assets']
    liabilities_df = ftx_recovery_model_xlsx['Liabilities']
    securities_df = ftx_recovery_model_xlsx['Securities']

    ftx_intl_crypto_df = ftx_recovery_model_xlsx['FTX International Crypto']
    ftx_us_crypto_df = ftx_recovery_model_xlsx['FTX US Crypto']
    ftx_international_related_party_df = ftx_recovery_model_xlsx['FTX International Related Party']
    ftx_us_related_party_df = ftx_recovery_model_xlsx['FTX US Related Party']
    alameda_df = ftx_recovery_model_xlsx['Alameda Crypto']
    venture_df = ftx_recovery_model_xlsx['Investments']

    dataframes = {
        "cash_df": cash_df,
        "assets_df": assets_df,
        "liabilities_df": liabilities_df,
        "ftx_intl_crypto_df": ftx_intl_crypto_df,
        "ftx_us_crypto_df": ftx_us_crypto_df,
        "ftx_international_related_party_df": ftx_international_related_party_df,
        "ftx_us_related_party_df": ftx_us_related_party_df,
        "alameda_df": alameda_df,
        "venture_df": venture_df,
        "securities_df" : securities_df,
    }

    return dataframes

def get_close_price(symbol, interval):
    # Append 'USDT' to the symbol
    symbol += 'USDT'

    # Calculate the date of yesterday
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_date = yesterday.strftime("%Y-%m-%d")

    # Try to read from the cache file
    try:
        with open('cache.json', 'r') as f:
            cache = json.load(f)

        # Check if the data for the symbol and date is in the cache
        if symbol in cache and yesterday_date in cache[symbol]:
            return cache[symbol][yesterday_date]
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file doesn't exist or is not valid JSON, create an empty cache
        cache = {}

    url = "https://api.binance.com/api/v3/klines"

    # Calculate the timestamp of the start of yesterday
    yesterday_start = datetime(yesterday.year, yesterday.month, yesterday.day, tzinfo=tz.tzutc())
    timestamp = int(yesterday_start.timestamp() * 1000)

    params = {
        'symbol': symbol,
        'interval': interval,
        'startTime': timestamp,
        'limit': 1
    }

    response = requests.get(url, params=params)
    data = response.json()

    # The close price is at index 4
    close_price = float(data[0][4])

    # Add the data to the cache and save it to the file
    if symbol not in cache:
        cache[symbol] = {}
    cache[symbol][yesterday_date] = close_price

    with open('cache.json', 'w') as f:
        json.dump(cache, f)

    # Binance's X-MBX-USED-WEIGHT-(interval) header tells us how much of our rate limit we've used in the past interval
    # If we've used more than 80% of our limit, sleep for a bit
    if int(response.headers.get('X-MBX-USED-WEIGHT-1m', 0)) > 960:
        print("Approaching rate limit, sleeping for a bit...")
        time.sleep(10)

    return close_price