import logging
import unittest
from time import time

from FinanceFunctions.TradeEntry import TradeEntryBuy, TradeEntrySell
from Helpers.const import TransactionType


class TestTradeEntry(unittest.TestCase):
    def setUp(self) -> None:
        self.logger=logging.getLogger()
        
    def test_initial_state_buy(self):
        trade_fee = 0.05 #%
        transaction_time=1000
        quantity=0.01
        coin_value=10000

        trade_entry = TradeEntryBuy(trade_fee=trade_fee, transaction_time=transaction_time, quantity=quantity, coin_value=coin_value)

        expected_transaction_cost = trade_entry.quantity * trade_entry.coin_value
        expected_transaction_cost += (expected_transaction_cost*trade_fee)/100

        self.assertEqual(TransactionType.buy, trade_entry.transaction_type)
        self.assertEqual(trade_fee, trade_entry._trade_fee)
        self.assertEqual(transaction_time, trade_entry.transaction_time)
        self.assertEqual(quantity, trade_entry.quantity)
        self.assertEqual(coin_value, trade_entry.coin_value)
        self.assertIsNotNone(trade_entry.id)

        self.assertEqual(expected_transaction_cost, trade_entry.transaction_cost)
        
        
    def test_initial_state_sell(self):
        # Arrange 
        trade_fee = 0.05 #%
        buy_transaction_time=1000
        sell_transaction_time=1010
        buy_quantity=0.01
        buy_coin_value=10000
        sell_coin_value=10050

        buy_trade_entry = TradeEntryBuy(
            trade_fee=trade_fee, 
            transaction_time=buy_transaction_time, 
            quantity=buy_quantity, 
            coin_value=buy_coin_value)

        sell_trade_entry = TradeEntrySell(
            trade_fee=trade_fee, 
            transaction_time=sell_transaction_time, 
            coin_value=sell_coin_value, 
            buy_trade_entries=buy_trade_entry)

        expected_transaction_gain = buy_trade_entry.quantity * sell_trade_entry.coin_value
        expected_transaction_gain -= (expected_transaction_gain*trade_fee)/100

        self.assertEqual(TransactionType.sell, sell_trade_entry.transaction_type)
        self.assertEqual(trade_fee, sell_trade_entry._trade_fee)
        self.assertEqual(sell_transaction_time, sell_trade_entry.transaction_time)
        self.assertEqual(buy_quantity, sell_trade_entry.quantity)
        self.assertEqual(sell_coin_value, sell_trade_entry.coin_value)
        
        self.assertIsNotNone(sell_trade_entry.id)
        self.assertEqual(buy_trade_entry.id, sell_trade_entry.linked_id)

        self.assertAlmostEqual(expected_transaction_gain, sell_trade_entry.transaction_gain, delta=1.4210854715202004e-14)


if __name__ == "__main__":
    unittest.main()