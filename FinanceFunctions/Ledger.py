from FinanceFunctions.TradeEntry import TradeEntryBuy, TradeEntrySell
from Helpers.const import TransactionType
from Helpers import DateHelper, MathHelper
from GetLogger import create_logger

class CoinLedger:
    def __init__(self, bfee=0.075):
        self._bfee = bfee
        self.logger = create_logger("ledger", "LOG_ledger.log")
        self.bank = 50 # 50 usd to spend
        self.available_coins = 0
        self.transaction_history = []
        self.min_percent_gain_allowed = 0.45
        
        # amount of coins to buy for x-value in main currency
        self.coin_value_to_buy = 10

    def default_purchase_quantity(self, coin_value):
        return (1/coin_value)*self.coin_value_to_buy

    def propose_sell(self, coin_sell_value, time_stamp, pct=-1):
        """
        pct: indicates how much of currently hold stock ought to be sold
        this is driven by trends
        -1 is to ignore and sell one transaction
        values between 0 - 1, 1 == 100%
        """
        # check what we have purchased
        # verify price is ok
        # act and sell
        human_date = DateHelper.get_datetime_single_from_ms(time_stamp)

        if len(self.transaction_history) == 0:
            # self.logger.info(f"propose_sell at {human_date}:{coin_sell_value} > EMPTY STOCK - quitting")
            return False
        
        matching_transactions = [k for k in self.transaction_history if k.active and k.coin_value < coin_sell_value]

        if len(matching_transactions) == 0:
            self.logger.info(f"{human_date}: propose_sell {coin_sell_value} > NO MATCHING STOCK - quitting")
            # self.logger.info([k.coin_value for k in self.transaction_history])
            return False

        matching_transactions.sort(key=lambda x: x.coin_value, reverse=True)

        # check the % increase on each
        percent_gains = MathHelper.percent_diff(coin_sell_value, matching_transactions)

        transaction_count_to_close = 1
        if pct > -1:
            transaction_count_to_close = round(len(matching_transactions) * pct)
        
        transactions_to_close = []
        for dx in range(transaction_count_to_close):
            max_percent_gain_value = percent_gains[dx]
        
            # self.logger.info(f"propose_sell: Matching len: {len(matching_transactions)}")
            closing_transaction: TradeEntryBuy = matching_transactions[dx]

            if max_percent_gain_value < self.min_percent_gain_allowed:
                self.logger.info(f"{human_date}: FAILED PERCENT CHECK {max_percent_gain_value}, {closing_transaction.coin_value} at: {coin_sell_value}")
                return False
            

            self.logger.info(f"{human_date}: ________________SELL:  {closing_transaction.coin_value} at: {coin_sell_value}. Gain: {max_percent_gain_value}")
            closing_transaction.active = False
            transactions_to_close.append(closing_transaction)
        
        # previously buy, now is being closed
        

        trade_entry = TradeEntrySell(self._bfee, time_stamp, coin_sell_value, transactions_to_close)
        
        self.bank += trade_entry.transaction_gain
        self.available_coins -= sum([k.quantity for k in transactions_to_close])
        self.transaction_history.append(trade_entry)
        
        return True

    def check_buy_good_to_proceed(self, buy_price, buy_timestamp):
        # check if new purchase is older than 1min from most recent
        # check if new purchas price is better by at least 0.5%
        #]most_recent_buy = 
        human_date = DateHelper.get_datetime_single_from_ms(buy_timestamp)

        recent_buys = [k for k in self.transaction_history if k.active]
        if len(recent_buys) == 0:
            return True

        last_buy_timestamp = max([k.transaction_time for k in recent_buys])
        
        # units ms
        if last_buy_timestamp + 60*1000 > buy_timestamp:
            self.logger.info(f"{human_date}: FAILED BUY CHECK: recent buy too recent: {DateHelper.get_datetime_single_from_ms(last_buy_timestamp)}")
            return False

        percent_diff = MathHelper.percent_diff(buy_price, recent_buys)
        test_result = all([k < 0 for k in percent_diff])
        if not test_result:
            self.logger.info(f"{human_date}: FAILED BUY CHECK: proposed buy {buy_price} with higher price than currently active.")
            return False
        return True


    def propose_buy(self, coin_buy_price, time_stamp, pct=-1):
        """
        if pct > 0, use it as multiplayer of standard amount per transaction (within the limit of remaining money)
        """
        if not self.check_buy_good_to_proceed(coin_buy_price, time_stamp):
            return

        human_date = DateHelper.get_datetime_single_from_ms(time_stamp)

        # for BTCUSDT price ~61935.29
        quantity_to_buy = self.default_purchase_quantity(coin_buy_price)

        trade_entry = TradeEntryBuy(self._bfee, time_stamp, quantity_to_buy, coin_buy_price)
        
        if self.bank < trade_entry.transaction_cost:
            self.logger.info(f"{human_date}: Insufficient funds, transaction no go: {coin_buy_price}")
            # raise Exception("No more funds in bank")
            return False

        self.bank -= trade_entry.transaction_cost
        self.available_coins += quantity_to_buy
        self.transaction_history.append(trade_entry)

        self.logger.info(f"{human_date}: ________________BUY at:{coin_buy_price}")

        return True

    def get_active_purchases(self):
        """
        returns unclosed purchases
        """
        return [k for k in self.transaction_history if k.transaction_type == TransactionType.buy and k.active]

    def sum_of_active_transactions(self):
        sell_value = 0
        # translate buys into sells, calculate gain including fee cost
        for active_transaction in self.get_active_purchases():
            sell_transaction = TradeEntrySell(self._bfee, 0, active_transaction.coin_value, [active_transaction])
            sell_value+=sell_transaction.transaction_gain
        
        return sell_value