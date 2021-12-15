import traceback
import time
from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager
from loguru import logger
from BlackBoxScripts.BinanceAllKlinesToNotification import ProcessData
from binanceHelper.BinanceClient import BinanceClient
# from binanceHelper.SamBinanceClient import AsyncClient


@logger.catch
def start_web_socket(processData:ProcessData):
    """
    listen to websocket, populate postgresql with result
    """
    coin_pairs = processData.api_client.get_usdt_symbols()
    websocket_manager = BinanceWebSocketApiManager(exchange="binance.com", output_default="dict")
    websocket_manager.create_stream('kline_1m', coin_pairs, stream_label="dict", output="dict")
    
    previous_time_stamp = 0
    while True:
        time_stamp = int(time.time())
        if (time_stamp%900 == 0 and previous_time_stamp < time_stamp):
            # health check
            logger.info(f"\nHEALTH CHECK --- Stored coin number: {len(processData.full_klines_data)}, (BTCUSDT): {len(processData.full_klines_data.get('BTCUSDT', []))}\n")
            previous_time_stamp = time_stamp

        if websocket_manager.is_manager_stopping():
            exit(0)

        data = websocket_manager.pop_stream_data_from_stream_buffer()
        
        if data is False:
            time.sleep(0.01)
            continue

        elif data is None:
            continue

        elif data.get("result", 1) is None:
            # odd case at the start when no result is given
            # dict: {'result': None, 'id': 1}
            continue

        try:
            processData.process_websocket_data(data)

        except Exception:
            logger.error(f"last kline: {data}")
            logger.error(traceback.format_exc())
            websocket_manager.stop_manager_with_all_streams()
            exit(1)

if __name__ == "__main__":
    # https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-streams

    logger.add("LOG_run_klines_notifications.log", format="{time:YYYY-MM-DDTHH:mm:ss} {level} {message}", level="INFO",  rotation="500 MB")
    testNet = False
    b_client = BinanceClient(testNet)
    # b_client = AsyncClient(testNet)
    processData = ProcessData(b_client)
    start_web_socket(processData)