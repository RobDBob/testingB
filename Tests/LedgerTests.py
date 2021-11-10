import logging
import unittest
from time import time

from FinanceFunctions.Ledger import CoinLedger
from Helpers.const import TransactionType


class TestLedger(unittest.TestCase):
    def setUp(self) -> None:
        self.logger=logging.getLogger()
        
    def _get_ledger(self):
        return CoinLedger(self.logger)

    def test_initial_state(self):
        ledger = self._get_ledger()

        self.assertEqual(0, len(ledger.transaction_history))
        self.assertEqual(50, ledger.bank)
        self.assertEqual(0, ledger.available_coins)
        
        self.assertEqual(10, ledger.coin_value_to_buy)
        self.assertEqual(0.1, ledger.default_purchase_quantity(100))

    def test_buy_transactions(self):
        # Arrange
        ledger = self._get_ledger()
        buy_price = [110, 112, 98, 95]
        
        # Action
        ledger.propose_buy(buy_price[0], time())
        ledger.propose_buy(buy_price[1], time())
        ledger.propose_buy(buy_price[2], time())
        ledger.propose_buy(buy_price[3], time())

        # Assert
        self.assertEqual(4, len(ledger.transaction_history))

        # one type transactions only
        self.assertEqual(1, len(set([k.transaction_type for k in ledger.transaction_history])))
        self.assertEqual(TransactionType.buy, ledger.transaction_history[0].transaction_type)

        # to verify those magic numbers
        self.assertEqual(9.969999999999999, ledger.bank)
        self.assertEqual(0.38749877941607264, ledger.available_coins)

    def test_sell_transactions(self):
        # Arrange
        ledger = self._get_ledger()
        buy_price = [110, 112, 98, 95]
        
        # Action
        ledger.propose_buy(buy_price[0], time())
        ledger.propose_buy(buy_price[1], time())
        ledger.propose_buy(buy_price[2], time())
        ledger.propose_buy(buy_price[3], time())
        ledger.propose_sell(115, time())

        # Assert
        self.assertEqual(5, len(ledger.transaction_history))

        # one type transactions only
        self.assertEqual(2, len(set([k.transaction_type for k in ledger.transaction_history])))


if __name__ == "__main__":
    unittest.main()