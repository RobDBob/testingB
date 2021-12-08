from time import sleep
from binance import Client

def function():
    client = getClient()
    while True:
        print(client.get_ticker(symbol="BTCUSDT"))
        sleep(5)

def getClient(test_net=False):
    from pathlib import Path
    from os import path
    import json
    with open(path.join(Path.home(), "binance.json")) as fp:
        b_config = json.loads(fp.read())
    if test_net:
        api_key = b_config["api_key_test"]
        api_secret = b_config["api_secret_test"]
    else:
        api_key = b_config["api_key"]
        api_secret = b_config["api_secret"]
    return Client(api_key=api_key_test, api_secret=api_secret_test, testnet=test_net)

if __name__ == "__main__":
    function()