import time

__all__ = ['time_of_date_to_timestamp', 'timestamp_to_time_of_date', 'local_time']


def time_of_date_to_timestamp(time_of_date, format='%Y-%m-%d-%H-%M-%S'):
    return time.mktime(time.strptime(time_of_date, format))


def timestamp_to_time_of_date(timestamp, format='%Y-%m%d-%H%M%S'):
    return time.strftime(format, time.localtime(timestamp))


def local_time():
    return time.strftime("%Y-%m%d-%H%M%S", time.localtime())
