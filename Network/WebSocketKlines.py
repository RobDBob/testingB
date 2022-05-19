import traceback
import time
from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager
from loguru import logger
from BlackBoxScripts.Processor_BinanceAllKlinesToNotification import Processor_BinanceAllKlinesToNotification
from Network.BinanceClient import BinanceClient
# from binanceHelper.SamBinanceClient import AsyncClient

@logger.catch
def start_web_socket(stable_coin: str, processData:Processor_BinanceAllKlinesToNotification):
    """
    listen to websocket, populate postgresql with result
    """
    channel_to_stream = 'kline_1m'
    coin_pairs = processData.api_client.get_symbols(stable_coin=stable_coin)
    websocket_manager = BinanceWebSocketApiManager(exchange="binance.com", output_default="dict")

    websocket_manager.create_stream(channel_to_stream, coin_pairs, stream_label="dict", output="dict")
    
    previous_time_stamp = 0
    while True:
        time_stamp = int(time.time())
        if (time_stamp%900 == 0 and previous_time_stamp < time_stamp):
            # health check
            logger.info(f"\nHEALTH CHECK --- Stored coin number: {len(processData.full_klines_data)}, (BTC{stable_coin}): {len(processData.full_klines_data.get(f'BTC{stable_coin}', []))}\n")
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