import psycopg2
import time

config = {"host":"192.168.1.34",
        "port":5555,
        "database":"testdb",
        "user":"postgres",
        "password":"postgres"}

def execute_query(sql, fetch=False, callback=None):
    """ Connect to the PostgreSQL database server """
    try:
        conn = psycopg2.connect(**config)
        with conn:
            with conn.cursor() as curs:
                curs.execute(sql)
                conn.commit()
                if fetch:
                    # callback with 100 rows at the time
                    if callback:
                        callback(iter_row(curs, 100))
                    else:
                        return curs.fetchall()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    finally:
        if conn is not None:
            conn.close()

def iter_row(curs, size=10):
    while True:
        rows = curs.fetchmany(size)
        if not rows:
            break
        for row in rows:
            yield row

def print_stuff(data_rows):
    print(len(list(data_rows)))
    print("_______________________")

def get_first_record():
    sql_select_first_record = 'SELECT * FROM "bpricesBTCUSDT" FETCH FIRST 1 ROW ONLY;'
    return execute_query(sql_select_first_record, fetch=True)[0]

def get_first_hour_records(first_record=None):
    first_record = first_record if not None else get_first_record()
    sql_select_records_between = 'select * from "bpricesBTCUSDT" bb where bb."timestamp"  >= {0} and bb."timestamp" < {1};'
    query_result = execute_query(sql_select_records_between.format(first_record[0], first_record[0]+3600), fetch=True)
    print(f"get_first_hour_records count: {len(query_result)}")
    return query_result

def get_all_after_first_hour_records(first_record=None):
    first_record = first_record if not None else get_first_record()
    timestamp = first_record[0]+3600
    return get_records_after_timestamp(timestamp)

def get_records_after_timestamp(timestamp):
    """
    timestamp: epoch secs
    """
    sql_select_records_after = 'select * from "bpricesBTCUSDT" bb where bb."timestamp"  >= {0};'
    query_result = execute_query(sql_select_records_after.format(timestamp), fetch=True)
    print(f"get_records_after_timestamp, timestamp: {get_records_after_timestamp}; record count: {len(query_result)}")
    return query_result