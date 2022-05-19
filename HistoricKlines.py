
from Network.WebSocketKlines import start_web_socket
from loguru import logger
from BlackBoxScripts.Processor_BinanceAllKlinesToNotification import Processor_BinanceAllKlinesToNotification
from BlackBoxScripts.Processor_BinanceAllKlinesDisplay import Processor_BinanceAllKlinesDisplay
from Network.BinanceClient import BinanceClient
# from binanceHelper.SamBinanceClient import AsyncClient



if __name__ == "__main__":
    # https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-streams

    logger.add("LOG_run_klines_notifications.log", format="{time:YYYY-MM-DDTHH:mm:ss} {level} {message}", level="INFO",  rotation="500 MB")
    testNet = False
    start_time_seconds = 163838534 # 21/12/01
    start_time_seconds = 1646161341 # 22/03/01
    b_client = BinanceClient(testNet)
    data = b_client.get_historical_klines("PORTOUSDT", startTime=start_time_seconds, interval="4h")
    print(data)
