import pandas_ta as ta

from Helpers.ScriptArguments import CreateScriptArgs
from binance import ThreadedWebsocketManager, helpers
from Playground.bFinanceAPIFunctions import getClient
import pandas as pd
from datetime import datetime
import TestScenarios

from MathFunctions.TATesting import TATester
from Helpers import const, APIHelper, DateHelper
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
    
    def _get_datetime_series(self, date_time_stamps_ms):
        # print(f"---- type: {type(date_time_stamps_ms)}, value: {date_time_stamps_ms}")
        return pd.to_datetime(date_time_stamps_ms, unit='ms').dt.strftime(const.date_time_format)

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
    from ReadFromPostgreSQL import execute_query
    from MathFunctions.TATesting import TATester
    from PriceWatcher import PriceWatcher
    from SignalTrigger import SignalTrigger

    sql_select_first_record = 'SELECT * FROM "bpricesBTCUSDT" FETCH FIRST 1 ROW ONLY;'
    sql_select_first_hour = 'select * from "bpricesBTCUSDT" bb where bb."timestamp"  >= {0} and bb."timestamp" < {1};'
    sql_select_remaining = 'select * from "bpricesBTCUSDT" bb where bb."timestamp"  >= {0};'
    
    first_record = execute_query(sql_select_first_record, fetch=True)[0]
    print(first_record[0])

    first_hour_records = execute_query(sql_select_first_hour.format(first_record[0], first_record[0]+3600), fetch=True)
    remaining_records = execute_query(sql_select_remaining.format(first_record[0]+3600), fetch=True)

    print(len(first_hour_records))
    print(len(remaining_records))

    # get first hour records on 1min interval
    first_hour_records_1m_interval = [k for k in first_hour_records if not k[0]%60]
    print(len(first_hour_records_1m_interval))

    initial_df = pd.DataFrame().from_records(first_hour_records_1m_interval)
    initial_df=initial_df.astype('float64')
    initial_df.columns=['dateTime', 'open', 'high', 'low', 'close', 'volume', 'numberOfTrades']
    initial_df.dateTime = initial_df.dateTime * 1000
    initial_df.set_index('dateTime', inplace=True)

    incoming_data = pd.DataFrame.from_records(remaining_records)
    incoming_data=incoming_data.astype('float64')
    incoming_data.columns=['dateTime', 'open', 'high', 'low', 'close', 'volume', 'numberOfTrades']
    incoming_data.dateTime = incoming_data.dateTime * 1000
    incoming_data.set_index('dateTime', inplace=True)

    logger = create_logger("DataTest2", "LOG_Scenario_price_check_from_db.log")
    
    data_holder = HQBrain(kline_interval=args.interval, historic_data=initial_df, logger=logger)

    monitor_price = False
    log_flag_monitor_price = False
    
    price_watcher = PriceWatcher(data_holder, logger)
    signal_trigger = SignalTrigger(data_holder, logger)

    # for record in remaining_records:
    for dx in range(len(incoming_data)):
        new_df = incoming_data.iloc[[dx]]

        if data_holder.update_data_on_tick(new_df):
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

if __name__ == "__main__":
    args = CreateScriptArgs()
    # start_web_socket(args)
    run_test_on_existind_data_from_db(args)