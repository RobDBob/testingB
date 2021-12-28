from binance import ThreadedWebsocketManager
import psycopg2

config = {"host":"localhost",
        "port":5555,
        "database":"testdb",
        "user":"postgres",
        "password":"postgres"}

def execute_query(sql):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        conn = psycopg2.connect(**config)
        with conn:
            with conn.cursor() as curs:
                curs.execute(sql)
                conn.commit()

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

def process_msg(msg):
    """
    Save time stamp in seconds rather than miliseconds
    """
    sql = 'INSERT INTO "bpricesBTCUSDT" (timestamp, open , high , low, close, volume, numberoftrades) VALUES ({0})'
    sql=sql.format(f"{msg['E']/1000}, {float(msg['k']['o'])}, {float(msg['k']['h'])}, {float(msg['k']['l'])}, {float(msg['k']['c'])}, {float(msg['k']['v'])}, {float(msg['k']['n'])}")
    execute_query(sql)

def start_web_socket():
    """
    listen to websocket, populate postgresql with result
    """
    twm = ThreadedWebsocketManager(testnet=False)
    twm.daemon = True
    twm.start()
    twm.start_kline_socket(callback=process_msg, symbol="BTCUSDT")
    twm.join()

if __name__ == "__main__":
    # https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-streams
    start_web_socket()