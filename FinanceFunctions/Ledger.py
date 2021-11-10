from FinanceFunctions.TradeEntry import TradeEntryBuy, TradeEntrySell
from Helpers.const import TransactionType

class CoinLedger:
    def __init__(self, logger, bfee=0.075):
        self._bfee = bfee
        self.logger = logger
        self.bank = 50 # 50 usd to spend
        self.available_coins = 0
        self.transaction_history = []
        
        # amount of coins to buy for x-value in main currency
        self.coin_value_to_buy = 10

    def default_purchase_quantity(self, coin_value):
        return (1/coin_value)*self.coin_value_to_buy

    def propose_sell(self, coin_sell_value, dateTime):
        # check what we have purchased
        # verify price is ok
        # act and sell
        if len(self.transaction_history) == 0:
            self.logger.info(f"propose_sell at {dateTime}:{coin_sell_value} > EMPTY STOCK - quitting")
            return
        
        matching_transactions = [k for k in self.transaction_history if k.active and k.coin_value < coin_sell_value]

        if len(matching_transactions) == 0:
            self.logger.info(f"propose_sell at {dateTime}:{coin_sell_value} > NO MATCHING STOCK - quitting")
            self.logger.info([k.coin_value for k in self.transaction_history])
            return

        # check the % increase on each
        percent_gain = [((coin_sell_value/k.coin_value) - 1) for k in matching_transactions]
        best_gain_index = percent_gain.index(max(percent_gain))
        
        self.logger.info(f"propose_sell: Matching len: {len(matching_transactions)}")
        self.logger.info(f"propose_sell: Matching - best value: {matching_transactions[best_gain_index].coin_value}")
        
        # previously buy, now is being closed
        closing_transaction: TradeEntryBuy = matching_transactions[best_gain_index]
        trade_entry = TradeEntrySell(self._bfee, dateTime, coin_sell_value, closing_transaction)
        trade_entry.linked_id = closing_transaction.id
        
        self.bank += trade_entry.transaction_gain
        self.available_coins -= closing_transaction.quantity
        self.transaction_history.append(trade_entry)
        closing_transaction.active = False

    def propose_buy(self, coin_buy_price, dateTime):
        # logic to decide, if to buy

        # for BTCUSDT price ~61935.29
        quantity_to_buy = self.default_purchase_quantity(coin_buy_price)

        trade_entry = TradeEntryBuy(self._bfee, dateTime, quantity_to_buy, coin_buy_price)
        
        if self.bank < trade_entry.transaction_cost:
            self.logger.info(f"Insufficient funds, transaction no go")
            raise Exception("No more funds in bank")
            return

        self.bank -= trade_entry.transaction_cost
        self.available_coins += quantity_to_buy
        self.transaction_history.append(trade_entry)