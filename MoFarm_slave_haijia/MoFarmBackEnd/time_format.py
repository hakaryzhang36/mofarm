import datetime

def time_format():
    return '【' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f") + '】'