from loguru import logger

class TransactionManager:
    def __init__(self):
        self._records = {}

    def record_purchase(self, symbol,  tick_data, asks):
        # logger.info(f"{symbol}: RECORD PURCHASE: {asks}")
        self.records[symbol] = {"tick_data": tick_data, "asks": asks}


    @property
    def records(self):
        return self._records
    
    def check_trade_was_profitable(self, symbol, tick_data, bids):
        # what time lapse we are interested in
        # what percentage increase we are interested in
        # the moment it increases by 5% - sell
        # if it does not increase within 1hr - mark it as failed invest
        # stop loss? - 5% ??
        tick_event_time = tick_data["eventTime"] # in seconds
        
        recorded_tick = self.records[symbol]["tick_data"]
        
        purchase_time = recorded_tick["eventTime"]
        
        tick_prices =     f'Want S: H:{tick_data["high"]}, L:{tick_data["low"]}, O:{tick_data["open"]}, C:{tick_data["close"]}'
        pruchase_prices = f'Bought: H:{recorded_tick["high"]}, L:{recorded_tick["low"]}, O:{recorded_tick["open"]}, C:{recorded_tick["close"]}'

        # after 10min - emergency sell?
        emergency_sell_time = 10 * 60
        if purchase_time + emergency_sell_time < tick_event_time :
            logger.info(f"{symbol}: OUT OF TIME sell \n {tick_prices} \n {pruchase_prices}")
            logger.info(f"{symbol}: bids: {bids}\n")
            logger.info(f"{symbol}: asks: {self.records[symbol]['asks']}\n")

            del(self.records[symbol])

        # # stop loss, after 2min
        # stop_loss_time = 2 * 60
        # percentage_loss = 0.95
        # if (purchase_time + stop_loss_time < tick_event_time) and ( tick_close_price < purchase_price * percentage_loss):
        #     logger.info(f"{symbol}: STOP LOSS sell")
        #     del(self.records[symbol])

        # # good sell
        # percentage_gain = 1.1
        # if tick_close_price > purchase_price * percentage_gain:
        #     logger.info(f"{symbol}: GOOD sell")
        #     del(self.records[symbol])