class RecordedActions:
    def __init__(self):
        self._records = {}

    def record_purchase(self, symbol,  time_stamp, price):
        self.records[symbol] = (time_stamp, price)

    @property
    def records(self):
        return self._records