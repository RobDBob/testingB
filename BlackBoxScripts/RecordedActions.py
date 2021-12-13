class RecordedActions:
    def record_purchase(self, symbol,  time_stamp, price):
        self.transactions[symbol] = (time_stamp, price)