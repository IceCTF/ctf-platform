import datetime
def process(api, data):
    date = datetime.datetime.now() + datetime.timedelta(hours=-5)
    return date.day == 31 and date.month == 10, {}
