from BlackBoxScripts.BinanceAllKlinesToNotification import ProcessData
from BlackBoxScripts.BinanceAllKlinesToNotification import start_web_socket
from binanceHelper.BinanceClient import BinanceClient

if __name__ == "__main__":
    # https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-streams

    b_client = BinanceClient()

    processData = ProcessData(b_client)
    start_web_socket(processData)