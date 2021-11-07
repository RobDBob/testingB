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


if __name__ == "__main__":
    # 1636284300
    #  int(time.time())
    sql = 'select * from "bpricesBTCUSDT" bb where bb."timestamp" = 1636284259;'
    # execute_query(sql, fetch=True, callback=print_stuff)
    a = execute_query(sql, fetch=True)
    print(a[0])
    [print(type(k)) for k in a[0]]

    timestamp = a[0][0]
