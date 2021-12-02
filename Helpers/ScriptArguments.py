import argparse
from binance import enums

def CreateScriptArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--timeout', default=None, type=int)
    parser.add_argument('-s', '--symbol', default="BTCUSDT", type=str)
    parser.add_argument('-tn', '--test_net', action="store_true", default=False)
    parser.add_argument('-i', '--interval', default=enums.KLINE_INTERVAL_1MINUTE, type=str)

    args = parser.parse_args()

    print(f"arguments set to: {args}")
    return args