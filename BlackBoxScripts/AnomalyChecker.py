from loguru import logger

class AnomalyChecker:
    def __init__(self, vol_increase_x, not_increase_x, back_off_after_notification):
        self.vol_increase_x = vol_increase_x
        self.not_increase_x = not_increase_x
        self.back_off_after_notification = back_off_after_notification
        
        self.anomaly_detected_eventTime = {}
        
    def _get_pct_change(self, tick_data, average_data):
        if average_data > 0:
            return round((tick_data/average_data)*100, 4)
        return 0
        
    def check_activity_increased(self, symbol, symbol_kline_data, symbol_tick_data):
        volSMAValue_last_avg_value = round(float(symbol_kline_data.tail(1)["volSMA"].values[0]), 4)
        number_of_trades_last_avg_value = round(float(symbol_kline_data.tail(1)["NOTSMA"].values[0]), 4)
        
        volume_increased = volSMAValue_last_avg_value * self.vol_increase_x < symbol_tick_data["volume"]
        number_of_trades_increased = number_of_trades_last_avg_value * self.not_increase_x < symbol_tick_data["numberOfTrades"]
        
        if volume_increased and number_of_trades_increased:
            self.anomaly_detected_eventTime[symbol] = symbol_tick_data["eventTime"]
            
            vol_pct_change = self._get_pct_change(symbol_tick_data["volume"], volSMAValue_last_avg_value)
            number_of_trades_pct_change = self._get_pct_change(symbol_tick_data["numberOfTrades"], number_of_trades_last_avg_value)
            
            vol_msg = f"\nVOL: {volSMAValue_last_avg_value}->{symbol_tick_data['volume']}({vol_pct_change})%"
            trades_msg  = f"\nNOT: {number_of_trades_last_avg_value}->{symbol_tick_data['numberOfTrades']}({number_of_trades_pct_change})%"
            logger.info(f"{symbol}: at ${symbol_tick_data['close']}; {vol_msg}; {trades_msg}\n")
            return True
        return False
    
    
    def anomaly_already_detected_for_symbol(self, symbol, event_time):
        # logger.info(f"{get_datetime_single(time_stamp)}: anomally previously detected {symbol} - we are on the pause until after {self.anomaly_detected_eventTime[symbol] + self.back_off_after_notification}")
        return ( symbol in self.anomaly_detected_eventTime ) and ( self.anomaly_detected_eventTime[symbol] + self.back_off_after_notification > event_time)