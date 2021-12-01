from binance import ThreadedWebsocketManager
import psycopg2
import logging
from time import sleep

GET_TABLES_QUERY = "SELECT * FROM information_schema.tables where table_schema = 'public';"
CREATE_TABLE_QUERY = "CREATE TABLE public.{0} (timestamp int PRIMARY KEY,open decimal,close decimal,volume decimal,quotevolume decimal,lastvolume decimal);"

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
        self.sorted_data = {}
        self.previous_data = {}

        self.update_existing_tables_from_db()

    def process_msg(self, msg):
        """
        this method is the entry point with logic 
        Save time stamp in seconds rather than miliseconds
        """

        filtered_to_usdt_tokens = [k for k in msg if "usdt" in k["s"].lower()] 
        filtered_time_to_1m_sec_interval = [k for k in filtered_to_usdt_tokens if k["E"] % 60000 > 59500 or k["E"] % 60000 < 500] 
        if len(filtered_time_to_1m_sec_interval) == 0:
            
            return

        # logger.info(f"FILTERED: {filtered_time_to_1m_sec_interval}")

        clean_data = self.clean_up(filtered_time_to_1m_sec_interval)
        # logger.info(f"CLEAN: {clean_data}")
        self.save_data(clean_data)

    def clean_up(self, data):
        """
        purpose of this methos is to calculate: 
            - actual volume traded from 24hr rolling window to 1 min rolling period
            - open & close prices
        """
        clean_data = {}
        for coin_entry in data:
            coin_name = coin_entry["s"]

            if coin_name in self.previous_data:
                previous_data = self.previous_data[coin_name]
                clean_data[coin_name] = {
                    "E": coin_entry["E"],
                    "o": round(float(previous_data["o"]), 4),
                    "c": round(float(coin_entry["c"]), 4),
                    "v": round(float(coin_entry["v"]) - round(float(previous_data["v"])), 4),
                    "q": round(float(coin_entry["q"]) - round(float(previous_data["q"])), 4),
                    "Q": round(float(coin_entry["Q"]), 4),
                }
                # logger.info(f"PREVIOUS:{coin_name}: {previous_data}")
                # logger.info(f"CURRENT:{coin_name}: {coin_entry}")


            self.previous_data[coin_name] = coin_entry
        return clean_data

    def update_existing_tables_from_db(self):
        self.available_tables = [k[self.query_result_table_name_index] for k in execute_query(GET_TABLES_QUERY, fetch=True)]

    def create_table(self, table_name):
        execute_query(CREATE_TABLE_QUERY.format(table_name))
    
    def check_table_exists(self, table_name):
        return table_name in self.available_tables

    def make_sure_table_exists(self, expected_table_name):
        if not self.check_table_exists(expected_table_name):
            self.create_table(expected_table_name)
        
        self.update_existing_tables_from_db()
        if expected_table_name not in self.available_tables:
            sleep(1)
            self.update_existing_tables_from_db()
            return expected_table_name not in self.available_tables
        return True

    def save_data(self, clean_data):
        for coin_name in clean_data.keys():
            expected_table_name = f"ticker_{coin_name}".lower()
            if self.make_sure_table_exists(expected_table_name):
                time_stamp_secs = round(clean_data[coin_name]['E']/1000)
                opening_price = float(clean_data[coin_name]['o'])
                closing_price = float(clean_data[coin_name]['c'])
                volume = float(clean_data[coin_name]['v'])
                quoted_volume = float(clean_data[coin_name]['q'])
                last_volume = float(clean_data[coin_name]['Q'])
                
                values = f"{time_stamp_secs}, {opening_price}, {closing_price}, {volume}, {quoted_volume}, {last_volume}"
                sql_query = f'INSERT INTO "{expected_table_name}" (timestamp, open, close, volume, quotevolume, lastvolume) VALUES ({values})'
                execute_query(sql_query)


processData = ProcessData()

def start_web_socket():
    """
    listen to websocket, populate postgresql with result
    """
    twm = ThreadedWebsocketManager(testnet=False)
    twm.daemon = True
    twm.start()
    twm.start_ticker_socket(callback=processData.process_msg)
    twm.join()

if __name__ == "__main__":
    # https://binance-docs.github.io/apidocs/spot/en/#all-market-tickers-stream
  
    start_web_socket()
