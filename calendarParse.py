from icalevents.icalevents import events
import datetime

def getiCal():
    now = datetime.datetime.now().date()
    get_start = now - datetime.timedelta(days=31)
    get_end = now + datetime.timedelta(days=31)
    url = userReader()
    es  = events(url, fix_apple=True, sort=True, start=get_start, end=get_end)
    return es

def userReader():
    idfile = open('./userid.txt', 'r')
    rtn = idfile.readline()
    idfile.close()
    return rtn

if __name__ == '__main__':
    event = getiCal()
    for ev in event:
        print(ev.summary)
    print('done')