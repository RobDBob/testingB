from time import sleep
from Helpers.DBFunctions import execute_query

GET_TABLES_QUERY = "SELECT * FROM information_schema.tables where table_schema = 'public';"
CREATE_TABLE_QUERY = "CREATE TABLE public.{0} (timestamp int PRIMARY KEY,high decimal,low decimal,open decimal,close decimal,volume decimal,numberOfTrades decimal);"

class DBProgresSaver:
    query_result_table_name_index = 2

    def __init__(self):
        self.available_tables = None

        self.update_existing_tables_from_db()

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

    def save_data_to_db(self, data, symbol):
            # "high": round(float(incoming_message["data"]["k"]["h"]), 4), 
            # "low": round(float(incoming_message["data"]["k"]["l"]), 4), 
            # "open": round(float(incoming_message["data"]["k"]["o"]), 4), 
            # "close": round(float(incoming_message["data"]["k"]["c"]), 4), 
            # "volume": round(float(incoming_message["data"]["k"]["v"]), 4),
            # "eventTime": incoming_message["data"]["E"]/1000,
            # "numberOfTrades": incoming_message["data"]["k"]["n"]}

        expected_table_name = f"kline_{symbol.lower()}"

        if self.make_sure_table_exists(expected_table_name):
            values = f"{data['eventTime']}, {data['close']}, {data['high']},  {data['low']},  {data['open']},  {data['close']}, {data['numberOfTrades']}"
            sql_query = f'INSERT INTO "{expected_table_name}" (timestamp,high,low,open,close,volume,numberOfTrades) VALUES ({values})'
            execute_query(sql_query)
