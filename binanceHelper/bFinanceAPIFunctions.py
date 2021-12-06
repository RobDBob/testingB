from time import sleep
from binance import Client

def function():
    client = getClient()
    while True:
        print(client.get_ticker(symbol="BTCUSDT"))
        sleep(5)

def getClient(test_net=False):
    api_key_test = "fjwtEFGgh3rAO29WVPJ7IjQl3dN0Ml0147iLblPPZPQHsm6DGMkJ77LGQkLie20S"
    api_secret_test = "fSKO7rQtgWKePuLZf2IZuTYDl7RDZnniKUCoN9VAgQyjqsCKjza7ftQM00yEivkW"
    return Client(api_key=api_key_test, api_secret=api_secret_test, testnet=test_net)

if __name__ == "__main__":
    function()