from datetime import datetime
from Helpers import const


def get_datetime_single(date_time_stamp_ms):
    return datetime.utcfromtimestamp((int(date_time_stamp_ms)/1000)).strftime(const.date_time_format)