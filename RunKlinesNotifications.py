from Network.WebSocketKlines import start_web_socket
from loguru import logger
from BlackBoxScripts.BinanceAllKlinesToNotification import ProcessData
from Network.BinanceClient import BinanceClient
# from binanceHelper.SamBinanceClient import AsyncClient



if __name__ == "__main__":
    # https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-streams
    
    run_config ={
        "vol_increase_x": 15,
        "not_increase_x": 15,
        "back_off_after_notification": 3600,
        "max_kline_storage_count": 360,
        "ta_average_length": 60
    }


    logger.add("LOG_run_klines_notifications.log", format="{time:YYYY-MM-DDTHH:mm:ss} {level} {message}", level="INFO",  rotation="500 MB")
    testNet = False
    b_client = BinanceClient(testNet)
    # b_client = AsyncClient(testNet)
    processData = ProcessData(b_client, run_config)
    start_web_socket(processData)