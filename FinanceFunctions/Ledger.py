from FinanceFunctions.TradeEntry import TradeEntryBuy, TradeEntrySell
from Helpers.const import TransactionType
from Helpers import DateHelper

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

    def propose_sell(self, coin_sell_value, time_stamp):
        # check what we have purchased
        # verify price is ok
        # act and sell
        dateTime_human_utc = DateHelper.get_datetime_single_from_ms(time_stamp)
        if len(self.transaction_history) == 0:
            self.logger.info(f"propose_sell at {dateTime_human_utc}:{coin_sell_value} > EMPTY STOCK - quitting")
            return False
        
        matching_transactions = [k for k in self.transaction_history if k.active and k.coin_value < coin_sell_value]

        if len(matching_transactions) == 0:
            self.logger.info(f"propose_sell at {dateTime_human_utc}:{coin_sell_value} > NO MATCHING STOCK - quitting")
            self.logger.info([k.coin_value for k in self.transaction_history])
            return False

        # check the % increase on each
        percent_gain = [((coin_sell_value/k.coin_value) - 1) for k in matching_transactions]
        best_gain_index = percent_gain.index(max(percent_gain))
        
        self.logger.info(f"propose_sell: Matching len: {len(matching_transactions)}")
        closing_transaction: TradeEntryBuy = matching_transactions[best_gain_index]


        self.logger.info(f"________________SELL: on {dateTime_human_utc} {closing_transaction.coin_value} at: {coin_sell_value}. Gain: {100-(closing_transaction.coin_value/coin_sell_value)*100}%")
        
        # previously buy, now is being closed
        
        trade_entry = TradeEntrySell(self._bfee, time_stamp, coin_sell_value, closing_transaction)
        trade_entry.linked_id = closing_transaction.id
        
        self.bank += trade_entry.transaction_gain
        self.available_coins -= closing_transaction.quantity
        self.transaction_history.append(trade_entry)
        closing_transaction.active = False
        return True

    def propose_buy(self, coin_buy_price, time_stamp):
        dateTime_human_utc = DateHelper.get_datetime_single_from_ms(time_stamp)

        # for BTCUSDT price ~61935.29
        quantity_to_buy = self.default_purchase_quantity(coin_buy_price)

        trade_entry = TradeEntryBuy(self._bfee, time_stamp, quantity_to_buy, coin_buy_price)
        
        if self.bank < trade_entry.transaction_cost:
            self.logger.info(f"Insufficient funds, transaction no go")
            # raise Exception("No more funds in bank")
            return False

        self.bank -= trade_entry.transaction_cost
        self.available_coins += quantity_to_buy
        self.transaction_history.append(trade_entry)

        self.logger.info(f"________________BUY on: {dateTime_human_utc} at:{coin_buy_price}")

        return True

    def sum_of_active_transactions(self):
        sell_value = 0
        # translate buys into sells, calculate gain including fee cost
        for transaction in self.transaction_history:
            if not (transaction.transaction_type == TransactionType.buy and transaction.active):
                continue
            sell_transaction = TradeEntrySell(self._bfee, 0, transaction.coin_value, transaction)
            sell_value+=sell_transaction.transaction_gain
        
        return sell_value