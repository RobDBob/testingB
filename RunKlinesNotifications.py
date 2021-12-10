from BlackBoxScripts.BinanceAllKlinesToNotification import ProcessData
from BlackBoxScripts.BinanceAllKlinesToNotification import start_web_socket

if __name__ == "__main__":
    # https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-streams
    processData = ProcessData()
    start_web_socket(processData)