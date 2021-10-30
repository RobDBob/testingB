import pprint
from datetime import datetime
from .bFinanceAPIFunctions import getClient

def printResults(results):
    prices = [float(k["lastPrice"]) for k in results]
    print(prices)
    
    for idx in range(len(results)):
        timeStamp = int(results[idx]["id"])
        currentDateTime = datetime.utcfromtimestamp((timeStamp/1000)+3600).strftime('%Y-%m-%d %H:%M:%S')
        
        # ma2 = getMA(prices[:idx], 2)
        # ma4 = getMA(prices[:idx], 4)
        ma6 = getMA(prices[:idx], 6)
        ma6series = [float(results[idx-5]["lastPrice"]), float(results[idx-4]["lastPrice"]), float(results[idx-3]["lastPrice"]), float(results[idx-2]["lastPrice"]), float(results[idx-1]["lastPrice"]), float(results[idx]["lastPrice"])]
        print({currentDateTime: [results[idx]["lastPrice"], ma6, sum(ma6series)/6, prices[idx] > sum(ma6series)/6, prices[idx] > ma6]})
        # print(prices)
        # getMA(prices, 5)


def getMA(prices, length):
    """
    prices list must be last x-length from idx moment in time
    """ 
    # print(prices)
    lastXItemsWithLastPrice =  prices[len(prices)-length:]
    # lastXItemsWithOUTLastPrice =  prices[len(prices)-length-1:-1]
    return (sum(lastXItemsWithLastPrice))/length

def printAccountDetails():
    client = getClient()
    stuff = client.get_account()
    pprint.pprint(stuff)

def newStuff():
    import ta;

if __name__ == "__main__":
    printAccountDetails()