from datetime import datetime
import pytz
def convertTimeStringIntoSeconds(time):
    time = time.split(':')
    return int(time[0])*3600 + int(time[1])*60 + int(time[2])

def getOffSet(timezone_str):
    return pytz.timezone(timezone_str).utcoffset(datetime.now()).total_seconds()

def getDateObject(timestring):
    timestring = timestring.split(' ')
    date = timestring[0].split('-')
    time = timestring[1].split(':')
    time[2] = int(float(time[2]))
    return date, time

def getTimeOnly(time):
        return int(time[0])*3600 + int(time[1])*60 + int(time[2])

def getTimeStamp(timestring):
    date,time  = getDateObject(timestring)
    stamp = datetime(int(date[0]), int(date[1]), int(date[2]), int(time[0]), int(time[1]), int(time[2])).timestamp()
    return stamp

def getWeekDay(timestring):
    date,time  = getDateObject(timestring)
    return datetime(int(date[0]), int(date[1]), int(date[2])).weekday()

