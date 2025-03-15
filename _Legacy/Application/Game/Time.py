from pygame.time import Clock
from time import perf_counter as _getTime, sleep # can switch to normal time 
from ..Settings import FPS

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

if __debug__:
  last_frame_time = 0
  accurate_framerate = 0

def get_frameRate() -> float:
  global deltaTime
  return 1/deltaTime

def get_frameRateInt() -> int:
  global deltaTime
  return accurate_framerate.__trunc__()

def set_fixedDeltaTime(fdt:float):
  assert fdt >= 0
  if fdt < 0: return 
  global fixedDeltaTime
  fixedDeltaTime = fdt 

def init():
  global _prev_time,time,_start_time
  _start_time = _getTime()
  _prev_time = _start_time

def update():
  global frameCount,deltaTime,time,fixedDeltaTime,fixedTime,_prev_time,_start_time,_clock,last_frame_time, accurate_framerate
  frameCount += 1
  if frameCount % (FPS or 120) == 0:
    t = _getTime()
    accurate_framerate = (FPS or 120) / (t - last_frame_time)
    last_frame_time = t
  if FPS: 
    _clock.tick(FPS) #can be changed to .tick_busy_loop for MUCH more accurate timing
      
  #update dynamic time
  current_time = _getTime()
  deltaTime = current_time - _prev_time
  time = current_time - _start_time
  _prev_time = current_time
  #update fixed time
  fixedTime += fixedDeltaTime
  if __debug__:
    if 1/deltaTime < FPS/3:
      print("intense lag! -> Curr FPS:",1/deltaTime) 


if __name__ == '__main__':
  pass
