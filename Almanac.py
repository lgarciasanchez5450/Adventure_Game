#for date time
from time import time,perf_counter
from math import sin,pi,sqrt
from perlin import noise1,njit
three_pi_two = 3 * pi / 2
'''CC -> can change'''
@njit
def get_daylight(day_passed):
    d = sin(2*pi*day_passed+three_pi_two - .2)
    if d < 0:
        d = 0
    d = 1.3*sqrt(d)
    if d > 1:
        d = 1
    return d

class World_Almanac:
    def __init__(self):
        #setup
        self.months_in_year = 16#CC
        self.days_in_month = 25#CC
        self.hours_in_day = 24#CC
        self.minutes_in_hour = 60#CC
        self.seconds_in_minute = 60#CC
        self.do_seasons = True
        self.days_in_year = self.days_in_month * self.months_in_year
        self.seconds_in_year = self.seconds_in_minute * self.minutes_in_hour * self.hours_in_day * self.days_in_month * self.months_in_year
        self.seconds_in_month = self.seconds_in_minute * self.minutes_in_hour * self.hours_in_day * self.days_in_month
        self.seconds_in_day = self.seconds_in_minute * self.minutes_in_hour * self.hours_in_day 
        self.seconds_in_hour = self.seconds_in_minute * self.minutes_in_hour
        self.get_time = perf_counter #CC 
    
        #seasons setup
        self.seasons = ( 'summer', 'fall', 'winter','spring')
        self._season_offset = 0 #CC
        self.average_global_temperature = 60 # degrees fahrenheit, CC

        #stats
        self._year = 0
        self._month = 0
        self._day = 0
        self._hour = 0
        self._minute = 0
        self._second = 0

        self._year_passed = 0.0
        self._day_passed = 0.0

        self._time = 0
        self._start_time = 0
        self.time_speed = 1 #CC

    def start(self):
        self._time = self.get_time()
        self._start_time = self._time
        
    def set_time(self,year = None,month = None,day = None,hour = None,minute = None,second = None):

        assert isinstance(year,(int,type(None))) and isinstance(month,(int,type(None))) and isinstance(day,(int,type(None))) and isinstance(hour,(int,type(None))) and isinstance(minute,(int,type(None))) and isinstance(second,(int,type(None))), 'can only use integers!'
        self._start_time = self.get_time()
        self._start_time -= (year-1) * self.seconds_in_year if year is not None else 0
        self._start_time -= (month-1) * self.seconds_in_month if month is not None else 0
        self._start_time -= (day-1) * self.seconds_in_day if day is not None else 0
        self._start_time -= (hour-1) * self.seconds_in_hour if hour is not None else 0
        self._start_time -= minute * self.seconds_in_minute if minute is not None else 0
        self._start_time -= second if second is not None else 0
    
    def step_date(self,years = 0,months = 0,days = 0,hours = 0,minutes = 0,seconds = 0):
        added_time = 0
        added_time += years * self.seconds_in_year
        added_time += months * self.seconds_in_month
        added_time += days * self.seconds_in_day
        added_time += hours * self.seconds_in_hour
        added_time += minutes * self.seconds_in_minute
        added_time += seconds

        self._start_time -= added_time/self.time_speed
    
    @property
    def season_temperature(self):
        return sin(2*pi*self.raw_season+.775) ** 3 + noise1(self._year_passed*50)/20

    @property
    def day_temperature(self) -> float:
        return sin(2*pi*self._day_passed-pi/2)
    
    @property
    def temperature(self):
        return self.average_global_temperature + 10*self.day_temperature + 30*self.season_temperature
    
    @property
    def year(self): return self._year + 1
    @property
    def month(self): return self._month + 1
    @property
    def day(self): return self._day + 1
    @property
    def hour(self): return self._hour % 12 if self._hour != 0 or self._hour != 12 else 12
    @property
    def minute(self): return self._minute
    @property
    def second(self): return self._second
    @property
    def meridian_designation(self) -> str:
        if self._hour < 12:
            return 'AM'
        else:
            return 'PM'
    
    @property
    def season(self) -> str:
        return self.seasons[int(self.raw_season * len(self.seasons))] 

    @property
    def raw_season(self) -> float:
        '''A number [0,1] that is used to calculate what season it is '''
        return (self._year_passed + self._season_offset) % 1\
    
    @property
    def date(self) -> tuple:
        return (self.month,self.day,self.year)
    
    @property
    def daytime(self) -> tuple:
        return (self.hour,self.minute,self.second)
    
    @property
    def raw_time(self):
        self._time = self.get_time()
        return (self._time - self._start_time) * self.time_speed

    @property
    def daylight(self) -> float:
        '''[0,1], 0 -> night, 1 -> sunny'''
        return get_daylight(self._day_passed)
        

    def update(self):
        self._time = self.get_time()
        t =  (self._time - self._start_time) * self.time_speed
        self._year_passed = t%self.seconds_in_year/self.seconds_in_year
        self._day_passed = t%self.seconds_in_day/self.seconds_in_day
        #t is in seconds
        self._year = (t // self.seconds_in_year).__trunc__()
        t -= self._year * self.seconds_in_year

        self._month = (t // self.seconds_in_month).__trunc__()
        t -= self._month * self.seconds_in_month

        self._day = (t //  self.seconds_in_day).__trunc__()
        t -= self._day * self.seconds_in_day

        self._hour = (t // self.seconds_in_hour).__trunc__()
        t -= self._hour * self.seconds_in_hour

        self._minute = (t // self.seconds_in_minute).__trunc__()
        t -= self._minute *   self.seconds_in_minute

        self._second = t.__trunc__()

    def __str__(self):
        return f'{self.hour:02}:{self.minute:02}:{self.second:02} {self.meridian_designation}, {self.month:02}/{self.day:02}/{self.year:04}'

