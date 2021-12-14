from loguru import logger

class TransactionManager:
    def __init__(self):
        self._records = {}

    def record_purchase(self, symbol,  time_stamp, price):
        self.records[symbol] = (time_stamp, price)

    @property
    def records(self):
        return self._records
    
    def check_trade_was_profitable(self, symbol, data):
        if symbol not in self.records:
            return
        
        # what time lapse we are interested in
        # what percentage increase we are interested in
        # the moment it increases by 5% - sell
        # if it does not increase within 1hr - mark it as failed invest
        # stop loss? - 5% ??
        event_time = data["eventTime"] # in seconds
        current_price = data["close"]
        (purchase_time, purchase_price) = self.records[symbol]


        # after 10min - emergency sell?
        emergency_sell_time = 10 * 60
        if purchase_time + emergency_sell_time < event_time :
            logger.info(f"{symbol}: OUT OF TIME sell, purchase price: {purchase_price}, sell price {current_price}, diff {current_price-purchase_price}\n")
            del(self.records[symbol])

        # stop loss, after 2min
        stop_loss_time = 2 * 60
        percentage_loss = 0.95
        if (purchase_time + stop_loss_time < event_time) and ( current_price < purchase_price * percentage_loss):
            logger.info(f"{symbol}: STOP LOSS sell, purchase price: {purchase_price}, sell price {current_price}, diff {current_price-purchase_price}\n")
            del(self.records[symbol])

        # good sell
        percentage_gain = 1.1
        if current_price > purchase_price * percentage_gain:
            logger.info(f"{symbol}: GOOD sell, purchase price: {purchase_price}, sell price {current_price}, diff {current_price-purchase_price}\n")
            del(self.records[symbol])