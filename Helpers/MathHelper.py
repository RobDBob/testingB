def percent_diff(new_coin_value, transactions):
    return [((new_coin_value-k.coin_value)/k.coin_value*100) for k in transactions]