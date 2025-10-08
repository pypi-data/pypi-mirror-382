import datetime


def get_current_time(formt='%Y-%m-%d_%H:%M:%S'):
    return datetime.datetime.now().strftime(formt)


def get_current_date():
    return datetime.date.today().strftime('%Y-%m-%d')
