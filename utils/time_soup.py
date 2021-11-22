import datetime
from pytz import timezone    


def time_until_end_of_day(dt):
    return ((24 - dt.hour - 1) * 60 * 60) + ((60 - dt.minute - 1) * 60) + (60 - dt.second)

def datetime_to_seconds(dt):
    return (dt.hour * 3600) + (dt.minute * 60) + dt.second

def timedelta_to_datetime(dt):
    try:
        return datetime.datetime.strptime(str(dt), "%H:%M:%S")
    except:
        return datetime.datetime.strptime(str(dt)[7:], "%H:%M:%S")
    
def time_left_for_pacific_midnight():
    pa_time = datetime.datetime.now(timezone("US/Pacific"))
    pacific_time_in_sec = datetime.timedelta(seconds=time_until_end_of_day(pa_time))
    current_time_in_sec = datetime_to_seconds(datetime.datetime.now())
    midnight_of_pacific = datetime.timedelta(seconds=time_until_end_of_day(pa_time) + current_time_in_sec)
    
    time_left = timedelta_to_datetime(pacific_time_in_sec).strftime("%H hr %M min")
    midnight_time = timedelta_to_datetime(midnight_of_pacific).strftime("%H:%M")
    clock_time = datetime.datetime.strptime(midnight_time, "%H:%M").strftime("%I:%M %p")
    
    return time_left, clock_time

def timestamp():
    return datetime.datetime.now().strftime("%d/%m/%Y @ %I:%M %p")
