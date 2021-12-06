import psycopg2
import logging
from binance import enums
from binance import ThreadedWebsocketManager
from binanceHelper.bFinanceAPIFunctions import getClient
from time import sleep

GET_TABLES_QUERY = "SELECT * FROM information_schema.tables where table_schema = 'public';"
CREATE_TABLE_QUERY = "CREATE TABLE public.{0} (timestamp int PRIMARY KEY,close decimal,volume decimalc,numberOfTrades decimal,takerBaseVolume decimal,takerQuoteVolume decimal);"

# def create_logger(logger_name, file_name=None):
#     logger = logging.getLogger(logger_name)
#     logger.setLevel(logging.DEBUG)
#     file_handler = logging.FileHandler(file_name)
#     formatter    = logging.Formatter('%(asctime)s(%(levelname)s): %(message)s')
#     file_handler.setFormatter(formatter)
#     logger.addHandler(file_handler)
#     return logging.getLogger(logger_name)

# logger = create_logger(__name__, "LOG_binancealltickers.log")

config = {"host": "localhost",
        "port":5555,
        "database":"testdb",
        "user":"postgres",
        "password":"postgres"}

def execute_query(sql, fetch=False):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        conn = psycopg2.connect(**config)
        with conn:
            with conn.cursor() as curs:
                curs.execute(sql)
                conn.commit()
                if fetch:
                    return curs.fetchall()

    except psycopg2.errors.InFailedSqlTransaction:
        with conn:
            with conn.cursor() as curs:
                curs.execute("ROLLBACK")
                conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    finally:
        if conn is not None:
            conn.close()

class ProcessData:
    query_result_table_name_index = 2

    def __init__(self):
        self.available_tables = None

        self.update_existing_tables_from_db()

    def process_msg(self, msg):
        """
        this method is the entry point with logic
        Save time stamp in seconds rather than miliseconds
        """
        close_price = round(float(msg["data"]["k"]["c"], 4))
        number_of_trades = msg["data"]["k"]["n"]
        base_asset_volume = round(float(msg["data"]["k"]["v"], 4))
        taker_buy_base_asset_volume = round(float(msg["data"]["k"]["V"], 4))
        taker_buy_quote_asset_volume = round(float(msg["data"]["k"]["Q"], 4))
        complete_kline = msg["data"]["k"]["x"]

        if not complete_kline:
            return

        data = {
            "symbol": msg["data"]["s"],
            "klineEndTime": msg["data"]["k"]["T"]/1000,
            "close": close_price, 
            "numberOfTrades": number_of_trades, 
            "baseVolume": base_asset_volume, 
            "takerBaseVolume": taker_buy_base_asset_volume,
            "takerQuoteVolume": taker_buy_quote_asset_volume}

        self.save_data(data)

    def update_existing_tables_from_db(self):
        self.available_tables = [k[self.query_result_table_name_index] for k in execute_query(GET_TABLES_QUERY, fetch=True)]

    def create_table(self, table_name):
        execute_query(CREATE_TABLE_QUERY.format(table_name))

    def check_table_exists(self, table_name):
        return table_name in self.available_tables

    def make_sure_table_exists(self, expected_table_name):
        if not self.check_table_exists(expected_table_name):
            self.create_table(expected_table_name)
            return self.wait_for_table_to_exist(expected_table_name)
        return True

    def wait_for_table_to_exist(self, expected_table_name):
        self.update_existing_tables_from_db()
        if expected_table_name not in self.available_tables:
            sleep(1)
            self.update_existing_tables_from_db()
            return expected_table_name in self.available_tables
        return True

    def save_data(self, data):
        #  (timestamp int PRIMARY KEY,close decimal,volume decimalc,numberOfTrades decimal,takerBaseVolume decimal,takerQuoteVolume decimal);"
                    # "symbol": msg["data"]["s"],
            # "klineEndTime": msg["data"]["k"]["T"],
            # "close": close_price, 
            # "numberOfTrades": number_of_trades, 
            # "baseVolume": base_asset_volume, 
            # "takerBaseVolume": taker_buy_base_asset_volume,
            # "takerQuoteVolume": taker_buy_quote_asset_volume}

        expected_table_name = f"kline_{data['symbol'].lower()}"

        if self.make_sure_table_exists(expected_table_name):
            values = f"{data['klineEndTime']}, {data['close']}, {data['baseVolume']}, {data['numberOfTrades']}, {data['takerBaseVolume']}, {data['takerQuoteVolume']}"
            sql_query = f'INSERT INTO "{expected_table_name}" (timestamp, close, volume) VALUES ({values})'
            execute_query(sql_query)


processData = ProcessData()

def get_kline_steam_names():
    client = getClient(test_net=False)
    products = client.get_products()
    coin_pairs = [k["s"] for k in products["data"] if "USDT" in k["s"]]
    print(f"retrieved {len(coin_pairs)} coin pairs")
    return [f"{symbol.lower()}@kline_{enums.KLINE_INTERVAL_1MINUTE}" for symbol in coin_pairs]

def start_web_socket():
    """
    listen to websocket, populate postgresql with result
    """
    twm = ThreadedWebsocketManager(testnet=False)
    twm.daemon = True
    twm.start_multiplex_socket(callback=processData.process_msg, streams=get_kline_steam_names())
    twm.join(60)
    twm.stop()

if __name__ == "__main__":
    # https://binance-docs.github.io/apidocs/spot/en/#all-market-tickers-stream

    start_web_socket()