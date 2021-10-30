from time import sleep
from binance import Client

def function():
    client = getClient()
    while True:
        print(client.get_ticker(symbol="BTCUSDT"))
        sleep(5)

def getClient(test_net):
    api_key_test = "f1itPrLonskTkpBVZVasE8BodXjrGI3FVkAmnqr5CxIt4MtZhpIWoMRDx9ZGF8CL"
    api_secret_test = "PhhYD2agY19f8ZngoOR588ZsuBuKjONctjbABtNXXUXD8qMdw1EWMNYC4fTB2w6W"
    return Client(api_key=api_key_test, api_secret=api_secret_test, testnet=test_net)

if __name__ == "__main__":
    function()