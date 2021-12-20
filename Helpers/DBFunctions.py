import psycopg2
from Helpers.DateHelper import get_datetime_single_from_ms
from Helpers.GetLogger import create_logger

logger = create_logger(__name__, "LOG_DBFunctions.log")

config = {"host":"192.168.1.34",
        "port":5555,
        "database":"testdb",
        "user":"postgres",
        "password":"postgres"}

def execute_query(sql, fetch=False, callback=None):
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

def iter_row(curs, size=10):
    while True:
        rows = curs.fetchmany(size)
        if not rows:
            break
        for row in rows:
            yield row

def get_first_record():
    sql_select_first_record = 'SELECT * FROM "bpricesBTCUSDT" FETCH FIRST 1 ROW ONLY;'
    return execute_query(sql_select_first_record, fetch=True)[0]

def get_first_hour_records(first_record=None):
    first_record = first_record if not None else get_first_record()
    return get_records_between_timestamps(first_record[0], first_record[0]+3600)

def get_all_after_first_hour_records(first_record=None):
    first_record = first_record if not None else get_first_record()
    timestamp = first_record[0]+3600
    return get_records_after_timestamp(timestamp)

def get_records_between_timestamps(from_timestamp_s, to_timestamp_s):
    sql_select_records_between = f'select * from "bpricesBTCUSDT" bb where bb."timestamp"  > {from_timestamp_s} and bb."timestamp" < {to_timestamp_s};'
    query_result = execute_query(sql_select_records_between, fetch=True)
    print(f"get_records_between_timestamps {get_datetime_single_from_ms(from_timestamp_s*1000)} - {get_datetime_single_from_ms(to_timestamp_s*1000)} count: {len(query_result)}")
    return query_result

def get_records_after_timestamp(timestamp, tableName="bpricesBTCUSDT"):
    """
    timestamp: epoch secs
    """
    sql_select_records_after = f'select * from "{tableName}" bb where bb."timestamp"  >= {0};'
    query_result = execute_query(sql_select_records_after.format(timestamp), fetch=True)
    print(f"get_records_after_timestamp, timestamp: {get_datetime_single_from_ms(timestamp*1000)}; record count: {len(query_result)}")
    return query_result