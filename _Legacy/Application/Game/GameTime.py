#for date time
from typing import Literal
from ..Utils.Noise import noise1
from ..Utils.Math.Fast import njit
from time import perf_counter,sleep
from math import sin,pi,sqrt

__all__ = [
    'year',
    'month',
    'day',
    'hour',
    'minute',
    'second',
    'meridian_designation',
    'light',
    'season',
    'temperature'
]

@njit(cache=True)
def full_range_sqrt(x:float) -> float:
    if x < 0:
        return -sqrt(-x)
    else:
        return sqrt(x)
@njit(cache = True)
def _get_daylight(day_passed):
    d = sin(2*pi*day_passed+(3*pi/2) - .2)
    d = (full_range_sqrt(d))+1
    d /= 2
    if d < 0:
        d = 0
    if d > 1:
        d = 1
    return d

light = 1.0

#CC = can change

months_in_year = 16#CC
days_in_month = 25#CC
hours_in_day = 24#CC
minutes_in_hour = 60#CC
seconds_in_minute = 60#CC
days_in_year = days_in_month * months_in_year
seconds_in_year = seconds_in_minute * minutes_in_hour * hours_in_day * days_in_month * months_in_year
seconds_in_month = seconds_in_minute * minutes_in_hour * hours_in_day * days_in_month
seconds_in_day = seconds_in_minute * minutes_in_hour * hours_in_day 
seconds_in_hour = seconds_in_minute * minutes_in_hour
get_time = perf_counter #CC 

#seasons setup
seasons = ('summer', 'fall', 'winter','spring')
_season_offset = 0 #CC
average_global_temperature = 60 # degrees fahrenheit, CC

#stats
_year = 0
_month = 0
_day = 0
_hour = 0
_minute = 0
_second = 0
_year_passed = 0.0
_day_passed = 0.0
_time = 0
_start_time = 0
time_speed = 60*10 #CC


#public variables
year:int = 0
month:int = 0
day:int = 0
hour:int = 0
minute:int = 0
second:int = 0
meridian_designation:Literal['AM','PM'] = 'AM'

def start():
    global _time,_start_time
    _time = get_time()
    _start_time = _time
    
def set_time(year = None,month = None,day = None,hour = None,minute = None,second = None):
    global _start_time
    assert isinstance(year,(int,type(None))) and isinstance(month,(int,type(None))) and isinstance(day,(int,type(None))) and isinstance(hour,(int,type(None))) and isinstance(minute,(int,type(None))) and isinstance(second,(int,type(None))), 'can only use integers!'
    _start_time = get_time()

    _start_time -= (year-1) * seconds_in_year/time_speed if year is not None else 0
    _start_time -= (month-1) * seconds_in_month/time_speed if month is not None else 0
    _start_time -= (day-1) * seconds_in_day/time_speed if day is not None else 0
    _start_time -= (hour-1) * seconds_in_hour/time_speed if hour is not None else 0
    _start_time -= minute * seconds_in_minute/time_speed if minute is not None else 0
    _start_time -= second/time_speed if second is not None else 0

def step_date(years = 0,months = 0,days = 0,hours = 0,minutes = 0,seconds = 0):
    global _start_time
    added_time = 0
    added_time += years * seconds_in_year
    added_time += months * seconds_in_month
    added_time += days * seconds_in_day
    added_time += hours * seconds_in_hour
    added_time += minutes * seconds_in_minute
    added_time += seconds

    _start_time -= added_time/time_speed

def season_temperature():
    return sin(2*pi*((_year_passed + _season_offset) % 1)+.775) ** 3 + noise1(_year_passed*50)/20

def day_temperature() -> float:
    return sin(2*pi*_day_passed-pi/2)

def temperature():
    return average_global_temperature + 10*day_temperature() + 30*season_temperature()


def season() -> str:
    return seasons[int((_year_passed + _season_offset) % 1 * len(seasons))] 

def daylight() -> float:
    '''[0,1], 0 -> night, 1 -> sunny'''
    return min(max(0,1.2*sin(4.47*_day_passed-0.83)),1)
    return _get_daylight(_day_passed)
    


def update():
    global _time, _year_passed, _day_passed,_year,_month,_day,_hour,_minute,_second,year,month,day,hour,minute,second,meridian_designation
    _time = get_time()
    t =  (_time - _start_time) * time_speed
    _year_passed = t%seconds_in_year/seconds_in_year
    _day_passed = t%seconds_in_day/seconds_in_day
    #t is in seconds
    _year = (t // seconds_in_year).__trunc__()
    year = _year + 1
    t -= _year * seconds_in_year

    _month = (t // seconds_in_month).__trunc__()
    month = _month + 1
    t -= _month * seconds_in_month

    _day = (t //  seconds_in_day).__trunc__()
    day = _day + 1
    t -= _day * seconds_in_day

    _hour = (t // seconds_in_hour).__trunc__()
    hour =  12 if (_hour == 0 or _hour == 12) else _hour % 12
    t -= _hour * seconds_in_hour

    _minute = (t // seconds_in_minute).__trunc__()
    minute = _minute
    t -= _minute *   seconds_in_minute

    _second = t.__trunc__()
    second = _second
    if _hour < 12:
        meridian_designation =  'AM'
    else:
        meridian_designation = 'PM'


    # update the light_surface
    global light
    light = daylight()


def game_time() -> tuple:
    return (year,month,day,hour,minute,second,meridian_designation)



# if __name__ == '__main__':
#     set_time(2024,1,1,1,1,0)
#     while True:
#         update()
#         print(f"Time: {hour:>2}:{minute:>2} {meridian_designation}, Light: {light:.2f}, Temp: {temperature():.2f} Season Temp: {average_global_temperature + 30*season_temperature()}")
#         sleep(5)
