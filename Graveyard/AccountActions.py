from time import time
import argparse
from binanceHelper.bFinanceAPIFunctions import getClient
import pprint


def get_all_orders(client, symbol):
    pprint.pprint(client.get_all_orders(symbol=symbol))

def get_account(client):
    
    pprint.pprint(client.get_account(timestamp=(time()*1000)-2000))
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-tn' , '--test_net', default=True, action="store_true")
    parser.add_argument('-a', '--account', default=False, action="store_true")
    parser.add_argument('-lt', '--last_trades', default=False, action="store_true")
    parser.add_argument('-s', '--symbol', default="BTCUSDT", type=str)
    args = parser.parse_args()

    print(f"arguments set to: {args}")

    client = getClient(test_net=args.test_net)

    if args.account:
        get_account(client)

    if args.last_trades:
        get_all_orders(client, args.symbol)