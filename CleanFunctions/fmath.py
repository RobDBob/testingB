import json
import sys
import time
import datetime

# api_key = '<api_key'>
# api_secret = '<api_secret'>

tick_history = []

def update_tick_history(current_price, max_store_size):
    """
    stores last x-prices 
    """
    current_price = float(current_price)
    if len(tick_history) < max_store_size:
        tick_history.append(current_price)
    else:
        tick_history.pop(0)
        tick_history.append(current_price)

def get_ma_price(lookback=5):
    if len(tick_history) < lookback:
        ma_price = -1
    else:
        recent_tick_prices = tick_history[-lookback:]
        print("--------------------------")
        print(tick_history)
        print(recent_tick_prices)
        print("--------------------------")
        ma_price = sum(recent_tick_prices)/len(recent_tick_prices)

    return ma_price
