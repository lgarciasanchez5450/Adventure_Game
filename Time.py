from pygame.time import Clock
from time import perf_counter as _getTime # can switch to normal time 
import time as _time
from Constants import FPS
class Stopwatch:
  def __init__(self,function = _time.time):
    self.startTime = None
    self.extraTime = 0
    self.paused = False
    self.measurement = function

  def running(self):
    if self.startTime:
      return True
    else:
      return False
    
  def start(self):
    self.startTime = self.measurement()

  def stop(self) -> float:
    time = self.timeElapsed()
    self.paused = 0
    self.startTime = None
    self.extraTime = 0
    return time

  def timeElapsed(self) -> float:
    if not self.paused:
      return self.measurement() - self.startTime + self.extraTime
    elif self.paused:
      return self.extraTime
    
  def setTime(self,newVal):
    if not self.paused:
      self.startTime = self.measurement() - newVal
      self.extraTime = 0
    elif self.paused:
      self.extraTime = newVal

  def pause(self):
    if not self.paused:
      self.extraTime += self.measurement() - self.startTime
      self.paused = True

  def unpause(self):
    if self.paused:
      self.startTime = self.measurement()
      self.paused = False
  
  def reset(self):
    self.startTime, self.extraTime = self.measurement(), 0
  time = timeElapsed

frameCount:int = 0

deltaTime:float = 1.0
time:float = 0.0

#'fixed' prefix denotes that the time is running at its own rate. for physics and such
fixedDeltaTime:float = .1
fixedTime:float = 0.0

#misc
_prev_time:float = 0
_start_time:float = 0
_clock = Clock()


def get_frameRate() -> float:
    global deltaTime
    return 1/deltaTime

def get_frameRateInt() -> int:
    global deltaTime
    return (1/deltaTime).__trunc__()

def set_fixedDeltaTime(fdt:float):
    if fdt < 0: return 
    global fixedDeltaTime
    fixedDeltaTime = fdt

def init():
    global _prev_time,time,_start_time
    _start_time = _getTime()
    _prev_time = _start_time

def update():
    global frameCount,deltaTime,time,fixedDeltaTime,fixedTime,_prev_time,_start_time,_clock
    frameCount += 1
    if FPS: 
      _clock.tick(FPS) #can be changed to .tick_busy_loop for MUCH more accurate timing 
    #update dynamic time
    current_time = _getTime()
    deltaTime = current_time - _prev_time
    time = current_time - _start_time
    _prev_time = current_time
    #update fixed time
    fixedTime += fixedDeltaTime

if __name__ == '__main__':
  print(locals())