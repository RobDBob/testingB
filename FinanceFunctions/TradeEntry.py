from Helpers.const import TransactionType
import uuid


class TradeEntryBase:
    def __init__(self, trade_fee:float, transaction_time:int, quantity:float, coin_value:float, trasnaction_type:TransactionType):

        self._transaction_time = transaction_time
        self._quantity = quantity
        self._coin_value = coin_value
        self._trade_fee=trade_fee
        
        self._id = uuid.uuid4()
        self.transaction_type:TransactionType = trasnaction_type
        self.active = True

    @property
    def transaction_time(self):
        return self._transaction_time

    @property
    def quantity(self):
        return self._quantity

    @property
    def coin_value(self):
        return self._coin_value

    @property
    def id(self):
        return self._id

class TradeEntryBuy(TradeEntryBase):
    def __init__(self, trade_fee, transaction_time, quantity, coin_value):
        super().__init__(trade_fee, transaction_time, quantity, coin_value, TransactionType.buy)

    @property
    def transaction_cost(self):
        if self.transaction_type == TransactionType.buy:
            coin_cost = self.quantity * self.coin_value
            return coin_cost*(1 + self._trade_fee/100)
        return None

class TradeEntrySell(TradeEntryBase):
    def __init__(self, trade_fee, transaction_time, coin_value, buy_trade_entries):

        overall_quantity = sum([k.quantity for k in buy_trade_entries])
        
        # if sell action, this will link buy transaction
        super().__init__(trade_fee, transaction_time, overall_quantity, coin_value, TransactionType.sell)
        self.linked_ids = [k.id for k in buy_trade_entries]
        self.active = False
    
    @property
    def transaction_gain(self):
        if self.transaction_type == TransactionType.sell:
            coin_cost = self.quantity * self.coin_value
            return coin_cost*(1 - self._trade_fee/100)
        return None
