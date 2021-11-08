from Helpers.ScriptArguments import CreateScriptArgs
from binance import ThreadedWebsocketManager, helpers
from Playground.bFinanceAPIFunctions import getClient
import pandas as pd
from datetime import datetime
import TestScenarios

from MathFunctions.TATesting import TATester
from Helpers import const, APIHelper, DateHelper, PandaFunctions, DBFunctions 
from MathFunctions.TATesting import TATester
from PriceWatcher import PriceWatcher
from SignalTrigger import SignalTrigger
import logging
from GetLogger import create_logger

logger_name_detail = "WebSocketPriceUpdaterTester_detail"
create_logger(logger_name_detail, "LOG_TestRecords_detail.log")

logger_name_high_level = "WebSocketPriceUpdaterTester"
create_logger(logger_name_high_level, "LOG_TestRecords.log")

class HQBrain:
    def __init__(self, kline_interval, historic_data=None, logger=None):
        self.kline_interval = kline_interval

        if historic_data is None:
            self.df = pd.DataFrame()
        else:
            self.df = historic_data
        self.logger = logging.getLogger(logger_name_high_level)
        # self.taTester = TATester(logger_name_detail)
        self.taTester = TATester(logger)

    @property
    def current_datetime(self):
        return DateHelper.get_datetime_single_from_ms(self.df.index[-1])

    def do_stuff_with_klline(self, msg):
        df = self.convert_to_df_from_kline(msg)
        if (self.update_data_on_tick(df)):
            self.action_time()

    def action_time(self):
        test_result = TestScenarios.data_test_1(self.taTester, self.df)

        # set cannot have dups, so if list len is == 1, it contains an uniformed decision
        set_trade_result = set(test_result)

        if len(set_trade_result) > 1:
            "mixed messages, returning without action"
            return

        if const.TA.buy in set_trade_result:
            self.buy()
        elif const.TA.sell in set_trade_result:
            self.sell()

    def buy(self):
        last_loc = self.df.index[-1]
        self.logger.info(f"{self.df.loc[last_loc, 'dateTime']}: BUY at: {self.df.loc[last_loc, 'close']} ")

    def sell(self):
        last_loc = self.df.index[-1]
        self.logger.info(f"{self.df.loc[last_loc, 'dateTime']}: SELL at: {self.df.loc[last_loc, 'close']} ")

    def convert_to_df_from_kline(self, msg):
        data = {
            "dateTime": [msg['E']], 
            "open": [float(msg['k']['o'])], 
            "high": [float(msg['k']['h'])], 
            "low": [float(msg['k']['l'])], 
            "close": [float(msg['k']['c'])], 
            "volume": [float(msg['k']['v'])]}
        return self.convert_to_df(data)

    def convert_to_df(self, data):
        """
        data: dict
        key: string: column names
        value: list: column values
        """
        df = pd.DataFrame(data)
        df.set_index('dateTime', drop=False, inplace=True)
        df.dateTime = DateHelper.get_datetime_single_from_ms(df.dateTime)
        return df

    def update_data_on_tick(self, df):
        """
        index: single value, timeStamp
        """
        # ONLY UPDATE IF LANDS ON EXPECTED INTERVAL 
        interval_milliseconds = helpers.interval_to_milliseconds(self.kline_interval)
        id_time_stamp_near_interval = datetime.utcfromtimestamp(df.index[-1]/1000) > datetime.utcfromtimestamp((self.df.index[-1] + interval_milliseconds)/1000)
        
        if id_time_stamp_near_interval:
            self.df = self.df.append(df)
            return True
        else:
            # print(f"Updated: FALSE: {DateHelper.get_datetime_single_from_ms(msg['E'])} > {counted}")
            # print(f"ping________________________ {df.loc[df.index[-1], 'dateTime']}")
            return False


def start_web_socket(args):
    """
    Run program of initial data grab & websocket
    """
    client = getClient(test_net=args.test_net)
    historic_data = APIHelper.get_historical_data(client, args.symbol, timeWindowMinutes=60, kline_interval=args.interval)
    data_updater = HQBrain(kline_interval=args.interval, historic_data=historic_data)

    twm = ThreadedWebsocketManager(testnet=args.test_net)
    twm.daemon = True
    twm.start()
    twm.start_kline_socket(callback=data_updater.do_stuff_with_klline, symbol=args.symbol)
    twm.join(timeout=args.timeout)

def run_test_on_existind_data_from_file(args):
    """
    reads test data from file
    splits into initial set, and feed set
    each of feed data is converted:
    from DataFrame -> DataSeries -> Dictionary -> DataFrame because >.<
    """
    from MathFunctions.TATesting import TATester
    from PriceWatcher import PriceWatcher
    from SignalTrigger import SignalTrigger
    
    # test_df = pd.read_pickle("4weekWorthBTCUSDT1mLive.pkl")
    # test_df = pd.read_pickle("1dayWorthBTCUSDT1mLive.pkl")
    test_df = pd.read_pickle("1weekWorthBTCUSDT1mLive.pkl")
    initial_df = test_df[:60]
    incoming_data = test_df[60:]

    logger = create_logger("DataTest2", "LOG_Scenario_price_check.log")
    
    data_holder = HQBrain(kline_interval=args.interval, historic_data=initial_df, logger=logger)

    monitor_price = False
    log_flag_monitor_price = False
    
    price_watcher = PriceWatcher(data_holder, logger)
    signal_trigger = SignalTrigger(data_holder, logger)

    for dx in range(len(incoming_data)):
        new_df = incoming_data.iloc[[dx]]

        # if data_holder.update_data_on_tick(new_df):
        data_holder.df = data_holder.df.append(new_df)
        monitor_price = signal_trigger.check_bbvol() or signal_trigger.check_macd_asmode()
                
        if monitor_price:
            if log_flag_monitor_price is False:
                logger.info(f"{data_holder.current_datetime}: START WATCHING")
                log_flag_monitor_price = True
            
            monitor_price = price_watcher.recalculate_conditions()
            
            if monitor_price is False:
                logger.info(f"{data_holder.current_datetime}: STOP WATCHING \n")
                log_flag_monitor_price = False
                # change of price- what's the plan?

def run_test_on_existind_data_from_db(args):
    """
    reads test data from file
    splits into initial set, and feed set
    each of feed data is converted:
    from DataFrame -> DataSeries -> Dictionary -> DataFrame because >.<
    """
    first_record = DBFunctions.get_first_record()
    first_hour_records = DBFunctions.get_first_hour_records(first_record)
    remaining_raw_records = DBFunctions.get_all_after_first_hour_records(first_record)

    # get first hour records on 1min interval
    minutes_interval = int(helpers.interval_to_milliseconds(args.interval)/1000)
    first_hour_records_w_interval = [k for k in first_hour_records if not k[0] % minutes_interval]
    print(len(first_hour_records_w_interval))

    idf = PandaFunctions.get_df_from_db_records(first_hour_records_w_interval) # initial df
    ndf = PandaFunctions.get_df_from_db_records(remaining_raw_records) # next df

    logger = create_logger("DataTest2", "LOG_Scenario_price_check_from_db.log")
    data_hq = HQBrain(kline_interval=args.interval, historic_data=idf, logger=logger)

    monitor_price = False
    log_flag_monitor_price = False
    
    price_watcher = PriceWatcher(data_hq, logger)
    signal_trigger = SignalTrigger(data_hq, logger)

    # for record in remaining_records:
    for dx in range(len(ndf)):
        new_df = ndf.iloc[[dx]]

        if data_hq.update_data_on_tick(new_df):
            monitor_price = signal_trigger.check_bbvol() or signal_trigger.check_macd_asmode()
                    
            if monitor_price:
                if log_flag_monitor_price is False:
                    logger.info(f"{data_hq.current_datetime}: START WATCHING")
                    log_flag_monitor_price = True
                
                monitor_price = price_watcher.recalculate_conditions()
                
                if monitor_price is False:
                    logger.info(f"{data_hq.current_datetime}: STOP WATCHING \n")
                    log_flag_monitor_price = False
                    # change of price- what's the plan?

if __name__ == "__main__":
    args = CreateScriptArgs()
    # start_web_socket(args)
    run_test_on_existind_data_from_db(args)