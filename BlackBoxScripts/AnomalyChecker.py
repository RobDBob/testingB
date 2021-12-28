from loguru import logger

class AnomalyChecker:
    def __init__(self, run_config):
        self.run_config = run_config
        self.anomaly_detected_eventTime = {}
        
    def _get_pct_change(self, tick_data, average_data):
        if average_data > 0:
            return round((tick_data/average_data)*100, 4)
        return 0
        
    def check_activity_increased(self, historic_tick_data, symbol_tick_data, symbol):
        volSMAValue_last_avg_value = round(float(historic_tick_data.tail(1)["volSMA"].values[0]), 4)
        number_of_trades_last_avg_value = round(float(historic_tick_data.tail(1)["NOTSMA"].values[0]), 4)
        
        volume_increased = volSMAValue_last_avg_value * self.run_config["vol_increase_x"] < symbol_tick_data["volume"]
        number_of_trades_increased = number_of_trades_last_avg_value * self.run_config["not_increase_x"] < symbol_tick_data["numberOfTrades"]
        
        if volume_increased and number_of_trades_increased:
            self.anomaly_detected_eventTime[symbol] = symbol_tick_data["eventTime"]
            
            vol_pct_change = self._get_pct_change(symbol_tick_data["volume"], volSMAValue_last_avg_value)
            number_of_trades_pct_change = self._get_pct_change(symbol_tick_data["numberOfTrades"], number_of_trades_last_avg_value)
            
            vol_msg = f"\nVOL: {volSMAValue_last_avg_value}->{symbol_tick_data['volume']}({vol_pct_change})%"
            trades_msg  = f"\nNOT: {number_of_trades_last_avg_value}->{symbol_tick_data['numberOfTrades']}({number_of_trades_pct_change})%"
            logger.info(f"{symbol}: ============ : ANOMALY : at ${symbol_tick_data['close']}; {vol_msg}; {trades_msg}\n")
            return True
        return False
    
    
    def anomaly_already_detected_for_symbol(self, symbol, event_time):
        # logger.info(f"{get_datetime_single(time_stamp)}: anomally previously detected {symbol} - we are on the pause until after {self.anomaly_detected_eventTime[symbol] + self.back_off_after_notification_secs}")
        if symbol in self.anomaly_detected_eventTime:
            return self.anomaly_detected_eventTime[symbol] + self.run_config["back_off_after_notification_secs"] > event_time
        return False
