import datetime

def logger(string):
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' ' +string)
