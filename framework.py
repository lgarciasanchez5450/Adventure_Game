'''
Framework for building Graphical User Interfaces for existing applications\n
This has been used to make:\n
Ball Simulator (Physics Stuff)\n
Music Player (similar to Spotify)\n
Notes Application (trashy)
'''
# speedup by making <accepts> classmethod into an attribute because its almost four times as fast to access.!!! TODO TODO TODO TODO TODO
import threading, time
import colorsys as _colorsys
from pygame import gfxdraw
from math import sqrt, cos, sin, hypot,atan2,pi,acos,e,exp
from pygame import mixer
from pygame import Surface
from pygame import font
from pygame import init as pginit
from pygame import display
from pygame import image
from pygame import draw
from pygame import Rect
from pygame import event as events
from pygame.constants import *
from pygame import mouse
from pygame import scrap
from os.path import dirname, realpath
from pygame import error as PygameEngineError
from pygame import transform
from pygame import time as pg_time
from typing import Callable
import debug
import sys
if sys.platform == 'win32':
  from ctypes import windll
  def maximize_screen():
    HWND = display.get_wm_info()['window']
    windll.user32.ShowWindow(HWND, 3)
    del HWND

def arccos(x):
  '''Degrees version of acos''' 
  return acos(x) * 180 / pi

def rgb_to_hsv(r,g,b): 

  M = max(r, g, b)
  m = min(r, g, b)

  #And then V and S are defined by the equations

  V = M/255
  S = 1 - m/M  if M > 0 else 0

  #As in the HSI and HSL color schemes, the hue H is defined by the equations
  d = sqrt(r*r+g*g+b*b-r*g-r*b-g*b)
  H = arccos((r - g/2 - b/2)/d)  if g >= b else 360 - arccos( (r - g/2 - b/2)/d)  
  
def hsv_to_rgb(h,s,v): 
  h *= 360
  M = 255*v
  m = M*(1-s)

  #Now compute another number, z, defined by the equation

  z = (M-m)*(1-abs((h/60)%2-1))

  #Now you can compute R, G, and B according to the angle measure of H. There are six cases. 
  if 0 <= h < 60:
    R = M
    G = z + m
    B = m

  elif 60 <= h < 120:
    R = z + m
    G = M
    B = m

  elif 120 <= h < 180:
    R = m
    G = M
    B = z + m

  elif 180 <= h < 240:
    R = m
    G = z + m
    B = M

  elif 240 <= h < 300:
    R = z + m
    G = m
    B = M

  elif 300 <= h <= 360:
    R = M
    G = m
    B = z + m
  else:
    R = 0
    G = 0
    B = 0
  return round(R),round(G),round(B)

'''
Random facts about the time module
**mil = million**

time.perf_counter()
Very precise, changes at least 10mil times in 2.53 seconds
Very expensive, takes 2.53 seconds to call 10mil times
*Changes very quickly, should not be used for game clocks, but for performance measurements, dont call regularly in loop unless measuring performance


time.monotonic()
Low precise, changes about 108 times in 1.67 seconds
Very fast, takes about 1.67 seconds to call 10mil times
*Changes every few milliseconds, should be called to measure time longer than .1 seconds, regularly faster to call than time.time() but only by a tiny bit

time.time()
Medium precise, changes about 1712 time in 1.71 seconds
Very fast, takes about 1.71 seconds to call 10mil times
*Changes about every thousandth of a second, anything closer than that and its not useful anymore

time.process_time()
DONT USE THIS, IT IS WACKY AND DOES NOT GIVE THE TIME YOU NORMALLY WANT
the others will be sufficient, only use if you know what you're doing!
'''
'''
Optimization Checklist
#####converting lists and tuples#####
tuple to tuple is the fastest by far(x = tuple(<tuple data type>))
list to tuple is the 2nd fastest
tuple to list is 3rd fastest
list to list is just behind tuple to list

#####adding is faster than subtracting#####
#if you have a statement like
if x - y > z:
  dostuff()
#change it to
if x > y + z:
  dostuff()

#### if statements are faster than min(max(x,_min),_max) ###
if you are using min/max statements to check if a single number is out of bounds then
use if statements

#### converting floats to ints #####
if you are sure that the number is a float():
  1) bind float.__trunc__ to a local variable
  2) use the bound float.__trunc__ as a function that will return the int
  EX:
  >>> import random
  >>> float_to_int = float.__trunc__
  >>> a = random.random()
  >>> a = float_to_int(a)
  #note only works with builtins.float datatypes
if it might be a float or might be an int then do the same as above but instead of float.__trunc__, bind "int" so the global lookup is faster.

lastly if you dont even need an builtins.int data type just a floored number then use "x//1"
'''
'''

'''
def specify_platform(*supported_platforms):
  if sys.platform not in supported_platforms:
    if len(supported_platforms) == 1:
      raise RuntimeError(f'This program only supports {supported_platforms[0]}, not {sys.platform}')
    else:
      raise RuntimeError(f'This program only supports {supported_platforms}, not {sys.platform}')

def filePath():
  #might be able to optimize if i just use str manipulation on __file__ instead of os functions
  #but i dont know if it would continue to be portable across different os's
  return dirname(realpath(__file__))
tab_unicode = '\t'
back_unicode = '\x08'
enter_unicode = '\r'
delete_unicode = '\x7f'
escape_unicode = '\x1b'
paste_unicode = '\x16'
copy_unicode = '\x03'
WHEEL_SENSITIVITY = 7
lowerCaseLetters = {'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'}
upperCaseLetters = {'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'}
allLetters = lowerCaseLetters.union(upperCaseLetters)
numbers = {'1','2','3','4','5','6','7','8','9','0','.','-','\x08'}
positive_integers = {'1','2','3','4','5','6','7','8','9','0','\x08'}
scientific_notation = numbers.union({'e',})
miscCharacters = {'\x08',' '}
symbolCharacters = {',','`','~','!','@','#','$','%','^','&','*','(',')','_','+','-','=','{','}','[',']','|','\\',';',':','"','<','>','.','?','/','`',"'"}
fileNameFriendlyCharacters = allLetters.union(numbers).union(miscCharacters).union(symbolCharacters).difference({'<','>','|','/','\\','*',':','?','"'})
AllCharacters = allLetters.union(numbers).union(symbolCharacters).union(miscCharacters)
preInitiated = 0
mixer.music.paused = 0 #type: ignore
WIDTH, HEIGHT = (0,0)
minScreenX,minScreenY = 0,0
inputBoxSelected = False
fps:int = 60
clock:pg_time.Clock
keysThatIgnoreBoxSelected = set()
PATH = filePath()
log_path = 'log.txt'
MUSIC_END = USEREVENT + 1
currentSoundName = ''
number = int|float
dt = 0
def setFPS(newVal) -> None:
  global fps
  fps = newVal
def addKeysThatIgnore(newKey):
  keysThatIgnoreBoxSelected.add(newKey)
def set_WHEEL_SENSITIVITY(__value) -> None:
  global WHEEL_SENSITIVITY
  if isinstance(__value,int) and __value >= 0:
    global WHEEL_SENSITIVITY
    WHEEL_SENSITIVITY = __value
  else:
    raise TypeError(f'WHEEL_SENSITIVITY does not support type: {type(__value)} or value: {__value} ')
def get_wheel_sesitivity() -> int:
  return WHEEL_SENSITIVITY
def py_line(surface, color, start_pos, end_pos, width=1):
    """ Draws wide transparent anti-aliased lines. Python implementation"""
    #if width == 0:return
    assert width != 0, 'argument <width> was passed with a value of 0'

    x0, y0 = start_pos
    x1, y1 = end_pos
    midpnt_x, midpnt_y = (x0+x1)/2, (y0+y1)/2  # Center of line segment.
    length = hypot(x1-x0, y1-y0)
    angle = atan2(y0-y1, x0-x1)  # Slope of line.
    width2, length2 = width/2, length/2
    sin_ang, cos_ang = sin(angle), cos(angle)

    width2_sin_ang  = width2*sin_ang
    width2_cos_ang  = width2*cos_ang
    length2_sin_ang = length2*sin_ang
    length2_cos_ang = length2*cos_ang

    # Calculate box ends.
    ul = (midpnt_x + length2_cos_ang - width2_sin_ang,
          midpnt_y + width2_cos_ang  + length2_sin_ang)
    ur = (midpnt_x - length2_cos_ang - width2_sin_ang,
          midpnt_y + width2_cos_ang  - length2_sin_ang)
    bl = (midpnt_x + length2_cos_ang + width2_sin_ang,
          midpnt_y - width2_cos_ang  + length2_sin_ang)
    br = (midpnt_x - length2_cos_ang + width2_sin_ang,
          midpnt_y - width2_cos_ang  - length2_sin_ang)

    gfxdraw.aapolygon(surface, (ul, ur, br, bl), color)
    gfxdraw.filled_polygon(surface, (ul, ur, br, bl), color)

class SoundError(BaseException):
  '''Error with pygame.mixer.music module'''
  pass


class Input:
  '''
  A way to dump all the input gathered by getAllInput() so that it can be directly put into
  update methods so that they can smartly pick what they need to update things.'''
  #return Input((mouse.get_pos(),mouse.get_pressed(),scrollUp-scrollDown,mbd,mbu),(keyDownQueue,keyUpQueue),flagsRaised)
  #mState = mpos, buttons, wheel, downs, ups
  def __init__(self,mState,KQueues,Events,dt):
    self.mState = mState
    try:
      self.Events = set(Events)    
      self.KDQueue = KQueues[0]
      self.KUQueue = KQueues[1]
      self.mpos:tuple[int,int]  =  mState[0]
      self.mousex:int  = mState[0][0]
      self.mousey:int  = mState[0][1]
      self.mb1:bool  =  mState[1][0]
      self.mb2:bool  =  mState[1][1]
      self.mb3:bool  =  mState[1][2]
      self.wheel:int  = mState[2]
      self.mb1down:bool  =  mState[3][0]
      self.mb2down:bool  =  mState[3][1]
      self.mb3down:bool  =  mState[3][2]
      self.mb1up = mState[4][0]
      self.mb2up = mState[4][1]
      self.mb3up = mState[4][2]
      self.dt = dt
      self.quitEvent = False
    except TypeError:
      self.quitEvent = True

  def __getattr__(self, __name: str):
    return self.__dict__[__name]
  
  def get_all(self,list_of_things) -> list:
    return [self.__dict__[item] for item in list_of_things]

class QuickWheel:
  @classmethod
  def accepts(cls):
    return ('KDQueue','KUQueue','mpos','mb1down','mb1up')
  def __init__(self,pos:tuple,options:tuple|list,key:str,radius:int,rot:float):
    self.pos = pos
    self.options = options
    self.key = key
    self.radius = radius
    self.on = False
    amount = len(options)
    for num,option in enumerate(self.options):
      option:Button
      option.x = int(self.radius * cos(num*2*pi/amount+rot) + pos[0]-option.xlen/2)
      option.y = int(self.radius * sin(num*2*pi/amount+rot) + pos[1]-option.ylen/2)

  def update(self,things):
    KDQueue,KUQueue,mpos,mb1down,mb1up = things
    if self.key in KDQueue: self.on = True
    if self.key in KUQueue: self.on = False
    if self.on: 
      for option in self.options:
        option:Button
        option.update((mpos,mb1down,0,(),mb1up))

  def draw(self):
    if not self.on: return
    for option in self.options:
      option:Button
      option.draw()

class TitleScreen:
  def __init__(self,screen_time:int|None = None,fps = 60):
    self._fps = fps
    self._background_color = (0,0,0)
    self._rect = Rect(0,0,WIDTH,HEIGHT)
    self._screen_time = screen_time
    self._defaults = {}
    self._start_time = None
    self._title_done = False
    ###self._defaults setter should go last
    self.clock = pg_time.Clock()
    self._defaults = {name for name in self.__dict__}

  def stop_early(self) -> None:
    self._title_done = True

  @property
  def TitleDone(self):
    return self._title_done
  @property
  def background_color(self):
    self._background_color
  @background_color.setter
  def background_color(self,newColor):
    if not isinstance(newColor,tuple): raise TypeError("Has to be a tuple!")
    if len(newColor) != 3: raise TypeError("Color assignment is (R,G,B) (no A)!")
    for color in newColor:
        if not (0<= color <= 255): raise TypeError("Color range is not within bounds!")
    self._background_color = newColor
  
  #__setattr__ is unecesary cause there is no offsetPos to set for each draw_obj
  def start(self):
    thread = threading.Thread(target=self._start)
    thread.start()

  def _start(self):
    self._start_time = time.monotonic()
    while 1:
      if self._screen_time and time.monotonic() - self._start_time > self._screen_time or self._title_done: #time has run out
        self._title_done = 1
        break
      else:
        self.update(getAllInput())
        self.draw()
        display.flip()
        self.clock.tick(self._fps)


  def update(self,myInput:Input):
    for object in self.__dict__:
      if object not in self._defaults:
        objInput = myInput.get_all(self.__dict__[object])
        self.__dict__[object].update(objInput)

  def draw(self):
    draw.rect(screen,self._background_color,self._rect)
    for drawThing in self.__dict__:
      if drawThing not in self._defaults:
        self.__dict__[drawThing].draw()


class Image:
  @classmethod
  def accepts(cls) -> tuple:
    return ()
  
  def __init__(self,pos:tuple,image:Surface):
    self._pos = tuple(pos)
    self.image = image
    self.offSetPos = (0,0)
    self.pos = tuple(pos)

  @property
  def pos(self):
    return self._pos

  @pos.setter
  def pos(self,newVal):
    self._pos = newVal
    self._offSetPos = (0,0)
    self.tpos = (self.offSetPos[0]+newVal[0],self.offSetPos[1]+newVal[1])

  @property
  def offSetPos(self):
    return self._offSetPos
  
  @offSetPos.setter
  def offSetPos(self,newVal):
    self._offSetPos = newVal
    self.tpos = (self.pos[0]+newVal[0],self.pos[1]+newVal[1])
  def update(self,_):
    pass

  def draw(self):
    screen.blit(self.image,self.tpos)
  
class ScreenSurface:
  @classmethod
  def accepts(cls) -> tuple:
    return ()
  def __init__(self,pos,size,color = (0,0,0)):
    self.pos = pos
    self.size = size
    self.color = color
    self.surf = Rect(pos[0],pos[1],size[0],size[1])
  @property
  def offSetPos(self):
    return self._offSetPos

  @offSetPos.setter
  def offSetPos(self,newVal):
    self._offSetPos = newVal
    self.surf = Rect(self.pos[0]+newVal[0],self.pos[1]+newVal[1],self.size[0],self.size[1])

  def update(self,*_):
    pass
  def draw(self):
    draw.rect(screen,self.color,self.surf)

class Debug:
  @classmethod
  def accepts(cls) -> tuple:
    return ()
  def __init__(self,measureFunc = time.perf_counter,performanceImpact = 30):
    self.frameCount = 0
    self.frameTimes = [measureFunc(),]
    self.measureFunc = measureFunc
    self.drawEvery = performanceImpact

  def update(self):
    self.frameCount += 1
    if self.frameCount % self.drawEvery == 0:
      self.frameTimes.append(self.measureFunc())
      print(int(self.drawEvery/(self.frameTimes[-1]-self.frameTimes[-2])))

  def draw(self):
    return
    if self.frameCount % self.drawEvery == 0:
      print(int(self.drawEvery/(self.frameTimes[-1]-self.frameTimes[-2])))

  def onQuit(self):
    FPSlist = [self.drawEvery/(self.frameTimes[x+1]-self.frameTimes[x]) for x in range(len(self.frameTimes)-1)]
    FPSlist.sort()
    sum = 0
    for fps in FPSlist:
      sum += fps
    sum /= len(FPSlist)
    print(f'Avg FPS: {round(sum,2)}')
    print(f'Min FPS: {round(FPSlist[0],2)}')
    print(f'Max FPS: {round(FPSlist[-1],2)}')
    print(f'Total Frames Updated: {self.frameCount}')

class TextBox:
  @classmethod
  def accepts(cls) -> tuple:
    return ()
  def __init__(self,pos,font,text,words_color,showing:bool = True):
    self.pos = pos
    self.font = font
    self.text = text
    self.words_color = words_color
    self.textsurface = self.font.render(self.text, True, self.words_color)
    self.offSetPos = (0,0)
    self.showing = showing

  def update_text(self) -> None:
    '''
    Update the rendered text to match self.text
    '''
    self.textsurface = self.font.render(self.text,True,self.words_color)
  
  def setText(self,newText) -> None:
    self.text = newText
    self.textsurface = self.font.render(self.text,True,self.words_color)
  set_text = setText

  def clear(self):
    self.setText('')

  def update(self,_) -> None:
    pass

  def set_showing(self,__value) -> None:
    self.showing = __value

  def show(self) -> None: 
    self.showing = True
  
  def hide(self) -> None: 
    self.showing = False

  def draw(self):
    if self.showing:
      screen.blit(self.textsurface,(self.pos[0] + self.offSetPos[0],self.pos[1] + self.offSetPos[1]))

class Options: #In Development
  def __init__(self,pos):
    self.options = dict()
    self.pos = pos
    self.font = font.SysFont("Courier New",20)

  def update(self):
    for num,option in enumerate(self.options):
      draw.rect(screen,(10,10,10),Rect(self.pos[0],self.pos[1]+num*30,70,30))
      screen.blit(self.font.render(option,True,(255,255,255)),(self.pos[0],self.pos[1]+num*30))

class Slider:
  @classmethod
  def accepts(cls) -> tuple:
    return ('mpos','mb1down','mb1up')
  def __init__(self,x,y,xlen,ylen,min,max,save_function,slider_color,ball_color,acceptsInput:bool = True,type:int = 1,passed_color:tuple[int,int,int]|None = (0,0,0),starting_value:int|None = None):
    self.x = x
    self.y = y
    self.xlen = xlen
    self.ylen = ylen
    self.min = min
    self.max = max
    self.value = min if starting_value is None else starting_value
    if starting_value is not None:
      save_function(starting_value)
    self.save_function = save_function
    self.countperpixel = (max-min)/xlen
    self.sliderx = int((self.value-self.min)/self.countperpixel)
    self.offSetPos = (0,0)
    self._rect = Rect(self.x-1,self.y-1,self.xlen+2,self.ylen+2)
    self.collider = Rect(self.x,self.y,self.xlen,self.ylen)
    self.acceptsInput = acceptsInput
    self.slider_color = slider_color
    self.ball_color = ball_color
    self.ball_pos = (self.sliderx+self.x+self._offSetPos[0],self.y+self.ylen/2+self._offSetPos[1])
    self.active = 0
    self.pactive = 0
    self.type = type
    self.passed_color = passed_color
    self.passed_rect = Rect(0,0,0,0)
    self.mouse_active = 0
    self.own_background = True if not isinstance(slider_color,Surface) else False

  def changeSliderLimits(self,newMin:int|None = None,newMax:int|None = None):
    if newMin is not None and newMin != self.max:
      self.min = newMin
    if newMax is not None and newMax != self.min:
      self.max = newMax
    
    self.countperpixel = (self.max-self.min)/self.xlen
    self.set_value(self.value)# recalculate ball, and passed_rect
  change_slider_limits = changeSliderLimits

  def onActivate(self):
    pass

  def onDeactivate(self):
    pass

  @property
  def offSetPos(self) -> tuple[int,int]:
    return self._offSetPos

  @offSetPos.setter
  def offSetPos(self,newVal) -> None:
    self._rect = Rect(self.x + newVal[0]-1,self.y+newVal[1]-1,self.xlen+2,self.ylen+2)
    self.collider = Rect(self.x + newVal[0],self.y+newVal[1],self.xlen,self.ylen)
    self._offSetPos = newVal
    self.ball_pos = (self.sliderx+self.x+self._offSetPos[0],self.y+self.ylen/2+self._offSetPos[1])


  def update(self,things):
    'mpos,mb1down,mb1up'
    if not self.acceptsInput: return 
    mpos,mb1down,mb1up = things
    if self.collider.collidepoint(mpos):
      self.mouse_active = 1
      if mb1down:
        self.active = 1
      elif mb1up:
        self.active = 0
    elif mb1down or mb1up: # if not colliding and mb1down or mb1up dont update
      self.mouse_active = 0
      self.active = 0
    else:
      self.mouse_active = 0
    
    if self.active and not self.pactive:
      self.onActivate()
    elif not self.active and self.pactive:
      self.onDeactivate()
    if self.active:
      self.sliderx = mpos[0] - self.x - self._offSetPos[0]
      newVal = int(self.sliderx*self.countperpixel)+self.min
      if newVal < self.min: newVal = self.min
      elif newVal > self.max - 1: newVal = self.max - 1
      if self.value != newVal:
        self.value = newVal
        self.save_function(self.value)
      if self.sliderx > self.xlen: self.sliderx = self.xlen
      elif self.sliderx < 0: self.sliderx = 0
      self.ball_pos = (self.sliderx+self.x+self._offSetPos[0],self.y+self.ylen/2+self._offSetPos[1])
      self.passed_rect = Rect(self.x+self._offSetPos[0],self.y+self._offSetPos[1],self.sliderx,self.ylen)
    self.pactive = self.active

  def draw(self):
    if self.own_background:
      draw.rect(screen,self.slider_color,self._rect,0,2)
    else:
      screen.blit(self.slider_color,(self.x+self._offSetPos[0],self.y+self._offSetPos[1]))
    if self.type == 1: #always show ball
      draw.circle(screen,self.ball_color,self.ball_pos,self.ylen)
    else: # show passed rect
      if self.passed_color:
        draw.rect(screen,self.passed_color,self.passed_rect,0,2) 
      if self.mouse_active: #show ball when mouse hovering
        draw.circle(screen,self.ball_color,self.ball_pos,self.ylen)
      
  def set_value(self,newValue):
    '''set the value of slider, if slider is currently active(being controlled) then does not work''' 
    if self.active: return
    if newValue > self.max - 1: newValue = self.max - 1
    elif newValue < self.min: newValue = self.min
    self.save_function(newValue)
    self.value = newValue
    self.sliderx = int((newValue-self.min)/self.countperpixel)
    self.ball_pos = (self.sliderx+self.x+self._offSetPos[0],self.y+self.ylen/2+self._offSetPos[1])
    self.passed_rect = Rect(self.x+self._offSetPos[0],self.y+self._offSetPos[1],self.sliderx,self.ylen)

class DesmosSlider:
  @classmethod
  def accepts(cls) -> tuple:
    return ('mpos','mb1down','mb1up','KDQueue')
  def __init__(self,pos,size,lower_limit,upper_limit,save_function,slider_color,ball_color,starting_value,scale=3,fontsize=20):
    self.lower_limit = lower_limit
    self.upper_limit = upper_limit
    end_box_sizex = scale * fontsize * 15/21 # ratio of width to height of font for numbers
    slider_end_box_space = 6
    sliderlen = size[0]-2*(end_box_sizex + slider_end_box_space)
    slideroffsetx = end_box_sizex + slider_end_box_space
    self.f = save_function
    self.slider = Slider(pos[0]+slideroffsetx,pos[1]+size[1]/3,sliderlen,size[1]/3,lower_limit,upper_limit,self.save_function,slider_color,ball_color,True,1,None,starting_value)
    self.min_box = InputBox(pos,(end_box_sizex,size[1]),'Lower',slider_color,scale,self.set_lower_limit,positive_integers,fontsize)
    self.max_box = InputBox((pos[0]+size[0]-end_box_sizex,pos[1]),(end_box_sizex,size[1]),'Upper',slider_color,scale,self.set_upper_limit,positive_integers,size[1])
    self.min_box.set_text(str(self.lower_limit))
    self.max_box.set_text(str(self.upper_limit))
  
  @staticmethod
  def str_to_int(string:str) -> int:
    try:
      return int(string)
    except ValueError:
      return 0

  def save_function(self,value):
    self.f(value)

  def set_lower_limit(self,new_lower_limit):
    new_lower_limit = self.str_to_int(new_lower_limit)
    if new_lower_limit >= self.upper_limit:
      new_lower_limit = self.upper_limit-1
    self.lower_limit = new_lower_limit
    self.slider.changeSliderLimits(new_lower_limit)

  def set_upper_limit(self,new_upper_limit):
    new_upper_limit = self.str_to_int(new_upper_limit)
    if new_upper_limit < self.lower_limit:
      new_upper_limit = self.lower_limit+1
    self.upper_limit = new_upper_limit
    self.slider.changeSliderLimits(None,new_upper_limit+1)
  
  def set_value(self,value):
    if value < self.lower_limit:
      self.set_lower_limit(value)
    elif value > self.upper_limit:
      self.set_upper_limit(value)
    else: # in between preexisting limits
      self.slider.set_value(value)


  @property
  def offSetPos(self) -> tuple:
    return self._offSetPos

  @offSetPos.setter
  def offSetPos(self,newVal) -> None:
    self._offSetPos = newVal
    self.slider.offSetPos = newVal
    self.min_box.offSetPos = newVal
    self.max_box.offSetPos = newVal

  def update(self,things):
    '''mpos,mb1d,mb1u,KDQ'''
    mpos,mb1down,mb1up,KDQueue = things
    self.slider.update((mpos,mb1down,mb1up))
    self.min_box.update((mpos,mb1down,KDQueue))
    self.max_box.update((mpos,mb1down,KDQueue))

  def draw(self):
    self.slider.draw()
    self.min_box.draw()
    self.max_box.draw()
  
class Dropdown:
  #TODO: make a slider go up and down next to dropdown
  @classmethod
  def accepts(cls) -> tuple:
    return ('mpos','mb1down','mb1up','wheel','mb3down')

  def __init__(self,pos,size,up_color,down_color,text_color,captions,outPutCommand,maxy,rightClickCommand = None,tpos = (0,0),spacing:int = 1, myfont = None ):
    self.pos = list(pos)
    self.size = tuple(size)
    self.up_color = up_color
    self.down_color = down_color
    self.text_color = text_color
    self.captions_command = captions
    self.empty_list = []
    self.captions = list(captions())
    self.mpos = [0,0]
    self.new_captions = []
    self.outPutCommand = outPutCommand
    self.font = font.SysFont('Courier New', 20) if myfont is None else myfont
    self.yscroll = 0
    self.mhover = 0
    self.pmhover = 0
    self.maxy = maxy
    self.tpos = tpos
    self.spacing = spacing
    self.rightClickCommand = rightClickCommand if rightClickCommand else None
    if self.captions:
      assert isinstance(self.captions[0],(str,Surface)), "weeer al gunna dai"
      if isinstance(self.captions[0],str):
        for caption in self.captions:
          self.new_captions.append(self.font.render(caption, True, self.text_color))
      elif isinstance(self.captions[0],Surface):
        self.new_captions = self.captions
    else: #empty list
      self.new_captions = []
    self.buttons = [Button((pos[0],pos[1]+count*size[1]*self.spacing),size[0],size[1],self.command,down_color,up_color,(min(up_color[0]+25,255),min(up_color[1]+25,255),min(up_color[2]+25,255)),caption,self.tpos[0],self.tpos[1],self.rightCommand,accepts_mb3=True if self.rightClickCommand else False) for count,caption in enumerate(self.new_captions)]
    self.offSetPos = (0,0)
    self.lenButtons = len(self.buttons)
    self._rect = Rect(self.pos[0],self.pos[1],self.size[0],self.maxy)

  @property
  def offSetPos(self) -> tuple:
    return self._offSetPos

  def setAllToUp(self):
    for button in self.buttons:
      button.setToUp()

  @offSetPos.setter
  def offSetPos(self,newVal):
    self._offSetPos = newVal
    self._rect = Rect(self.pos[0]+newVal[0],self.pos[1]+newVal[1],self.size[0],self.maxy)
    for button in self.buttons:
      button.offSetPos = newVal

  def command(self):
    top = self.mpos[1]-(self.pos[1]+self._offSetPos[1])+self.yscroll
    if self.spacing != 1: top +=1 
    bottom = self.size[1]*self.spacing
    self.outPutCommand(top//bottom)

  def onMouseEnter(self):
    pass
  def onMouseExit(self):
    pass

  def rightCommand(self):
    top = self.mpos[1]-(self.pos[1]+self._offSetPos[1])+self.yscroll
    if self.spacing != 1: top +=1 
    bottom = self.size[1]*self.spacing
    if self.rightClickCommand:
      self.rightClickCommand(top//bottom)

  def recalculate_options(self):
    self.captions = list(self.captions_command())
    self.new_captions = []
    if not self.captions: return
    assert isinstance(self.captions[0],(str,Surface)), "weeer al gunna dai"
    if isinstance(self.captions[0],str):
      for caption in self.captions:
        self.new_captions.append(self.font.render(caption, True, self.text_color))
    elif isinstance(self.captions[0],Surface):
      self.new_captions = self.captions
    self.buttons = [Button((self.pos[0],self.pos[1]+count*self.size[1]*self.spacing),self.size[0],self.size[1],self.command,self.down_color,self.up_color,(min(self.up_color[0]+25,255),min(self.up_color[1]+25,255),min(self.up_color[2]+25,255)),caption,self.tpos[0],self.tpos[1],self.rightCommand,None, not not self.rightClickCommand,) for count,caption in enumerate(self.new_captions)]
    self.lenButtons = len(self.buttons)
    if self.yscroll > self.size[1]*self.lenButtons-self.maxy:
      self.yscroll = self.size[1]*self.lenButtons-self.maxy
    if self.size[1]*self.lenButtons < self.maxy:
      self.yscroll = 0 
    for button in self.buttons:
      button.offSetPos = self._offSetPos
      button.offsetY = self.yscroll


  def update(self,things):
    '''mpos,mb1down,mb1up,wheelState,mb3down'''
    mpos,mb1down,mb1up,wheelState,mb3down = things
    if self._rect.collidepoint(mpos):  
      if not self.pmhover:
        self.onMouseEnter()
      self.mhover = 1
      self.mpos = tuple(mpos)
      if self.size[1]*self.lenButtons >= self.maxy + self.yscroll and wheelState: #TODO: everything in this if statement can probably be optimized
        self.yscroll += wheelState * WHEEL_SENSITIVITY
        if self.yscroll + wheelState * WHEEL_SENSITIVITY > self.size[1]*self.lenButtons-self.maxy:
          self.yscroll = self.size[1]*self.lenButtons-self.maxy
        if self.yscroll < 0:
          self.yscroll = 0
        for button in self.buttons:
          button.offsetY = self.yscroll
          button.update((mpos,mb1down,mb3down,self.empty_list,mb1up))
      else:
        for button in self.buttons:
          button.update((mpos,mb1down,mb3down,self.empty_list,mb1up))
    else:
      self.mhover = 0
      if self.pmhover:
        self.onMouseExit()
        for button in self.buttons:
          button.setToUp()
    self.pmhover = self.mhover

  def draw(self):
    for button in self.buttons:
      #check if needs to be drawn
      if self.pos[1] + self._offSetPos[1] +button.offsetY> button.y+button._offSetPos[1]+button.ylen:
        continue
      if self.pos[1] + self._offSetPos[1]+self.maxy +button.offsetY< button.y+button._offSetPos[1]:
        continue
      button.draw()

  def __str__(self) -> str:
    return self.captions_command()
    
class LoadingBar:
  @classmethod
  def accepts(cls):
    return ()
  def __init__(self,pos,size,background_color,bar_color,border_color):
    self.pos = pos
    self.size = size
    self.background_color = background_color
    self.bar_color = bar_color
    self.border_color = border_color
    self.fullRect = Rect(pos[0]-2,pos[1]-1,size[0]+4,size[1]+2)
    self.max = 100
    self.position = 0
    self.loadedRect = Rect(pos[0],pos[1],self.position*self.size[0]/self.max,self.size[1])
    self.offSetPos = (0,0)


  @property
  def offSetPos(self):
    return self._offSetPos

  @offSetPos.setter
  def offSetPos(self,newVal):
    self._offSetPos = newVal
    self.fullRect = Rect(self.pos[0]+newVal[0]-2,self.pos[1]+newVal[1]-1,self.size[0]+4,self.size[1]+2)
    self.loadedRect = Rect(self.pos[0],self.pos[1],self.position*self.size[0]/self.max,self.size[1])


  def update(self,*_):
    pass

  def setPosition(self,newVal):
    if not isinstance(newVal,int):
      raise TypeError("Must be 'int' type")
    if newVal > 100:
      raise TypeError("Must not be greater than 100")
    if newVal < 0:
      raise TypeError("Must not be less than 0")
    self.position = newVal
    self.loadedRect = Rect(self.pos[0]+self._offSetPos[0],self.pos[1]+self._offSetPos[1],self.position*self.size[0]/self.max,self.size[1])

  def draw(self):
    draw.rect(screen,self.background_color,self.fullRect,0,2)
    draw.rect(screen,self.bar_color,self.loadedRect,0,2)
class InputBox:
  @classmethod
  def accepts(cls) -> tuple:
    return ('mpos','mb1down','KDQueue')
  def __init__(self,pos,size,caption = '',box_color = (100,100,100),max_chars=500,save_function = lambda x:x,restrict_input = None,fontSize = 21):
    self.pos = pos
    self.size = size
    self.font = font.SysFont('Courier New',fontSize)
    character = self.font.render('H',True,(0,0,0))
    self.character_x,self.character_y = character.get_size()
    del character
    self.active = False
    self.caption = caption
    self.box_color = box_color
    self.max_chars = max_chars
    self.chars = 0
    self.text = ''
    self.textsurface = self.font.render(self.text, True, (0, 0, 0))
    self.textRect = Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    self.max_chars_per_line = self.size[0]//self.character_x
    self.save_function = save_function
    self.restrict_input = restrict_input
    self.offSetPos = (0,0)
    self.timeactive = 0
    self.cursor_rect = Rect(0,0,50,10)
  @property
  def offSetPos(self):
    return self._offSetPos

  @offSetPos.setter
  def offSetPos(self,newPos):
    self._offSetPos = newPos
    self.textRect = Rect(self.pos[0]+self.offSetPos[0],self.pos[1]+self.offSetPos[1],self.size[0],self.size[1])

  def set_text(self,new_text:str):
    assert isinstance(new_text,str), "arg <new_text> must be of type 'str'"
    '''Sets text and also calls save function on it'''
    self.chars = len(new_text)
    self.text = new_text
    self.save_function(self.text)
    
  def set_text_no_save(self,new_text:str) -> None:
    assert isinstance(new_text,str), "argument <new_text> must be of type <str>"
    '''Sets Texts witout calling save function on it'''
    self.chars = len(new_text)
    self.text = new_text
  
  def check_keys(self,key):
    if self.active and self.restrict_input and key in self.restrict_input:
      if key == back_unicode:
        if self.text:  #if self.text has any thing in it  
          self.text = self.text[:-1]
          self.chars -= 1
          self.save_function(self.text)
          return
      elif self.chars < self.max_chars: #has not reached max characters yet
        if key == '\r':
          self.text += '\n'
        else:
          self.text += key
        self.chars += 1 #previously, self.chars = len(self.text)
        self.save_function(self.text)

  def update(self,things):
    '''mpos,mb1down,keys'''
    mpos,mb1down,keys = things
    if self.textRect.collidepoint(mpos):
      if mb1down:
        self.active = True
        self.timeactive = time.monotonic()
    else:
      if mb1down:
        self.active = False
    global inputBoxSelected
    if self.active:
      thingy = self.text
      inputBoxSelected = True
      for key in keys:
        self.check_keys(key)
      if thingy != self.text: #if text has been updated
        self.timeactive = time.monotonic()
        self.cursor_rect = Rect(self.pos[0]+ (len(self.text)%self.max_chars_per_line)*self.character_x + self._offSetPos[0]+2,self.pos[1]+(len(self.text)//self.max_chars_per_line)*self.character_y + self._offSetPos[1]+2,3,self.character_y-3)
    else:
      inputBoxSelected = False
      
  def draw(self): 
    if not self.text:
      if self.box_color:
        draw.rect(screen,self.box_color,self.textRect)
      self.textsurface = self.font.render(self.caption, True, (100, 100, 100))
      screen.blit(self.textsurface,(self._offSetPos[0]+self.pos[0],self.pos[1]+self._offSetPos[1]))
      if self.active and not int(time.monotonic()-self.timeactive) % 2:
        draw.rect(screen,(0,0,0),self.cursor_rect)
    else:
      letters = [letter for letter in self.text]
      if self.box_color:
        draw.rect(screen,self.box_color,self.textRect)
      for char_num, letter in enumerate(letters):
        self.textsurface = self.font.render(letter, True, (0, 0, 0))
        letterx = self.pos[0]+(char_num%self.max_chars_per_line)*self.character_x
        screen.blit(self.textsurface,(letterx+self._offSetPos[0],self.pos[1]+((char_num//self.max_chars_per_line)*self.character_y)+self._offSetPos[1]))
      if self.active and not int(time.monotonic()-self.timeactive) % 2:
        draw.rect(screen,(0,0,0),self.cursor_rect)

class RoundButton:
    @classmethod
    def accepts(cls) -> tuple:
      return ('mpos','mb1','mb3down','KDQueue')
    def __init__(self,pos,radius,OnDownCommand,down_color,up_color,idle_color,surface = Surface((0,0)),textx = 0,texty = 0,rightClickCommand = None,key = None,accepts_mb3:bool = False, downCommand = None, OnUpCommand = None,keyCommand = 'OnDownCommand'):
      self.pos = pos
      self.radius = radius
      self.OnDownCommand = OnDownCommand
      self.downCommand = downCommand if downCommand else lambda:0
      self.OnUpCommand = OnUpCommand if OnUpCommand else lambda:0
      self.down_color = down_color
      self.up_color = up_color
      self.down = False
      self.previous_state = False
      self.idle_color = idle_color
      self.text = surface
      self.textx = textx
      self.texty = texty
      self.idle = False
      self.state = False
      self.offsetY = 0
      self.key = key
      self.accepts_mb3 = accepts_mb3
      self.rightClickCommand = self.exampleRightClick if rightClickCommand == None else rightClickCommand
      self.keyCommand = keyCommand
      self.offSetPos = (0,0)

    def exampleRightClick(self):
      print("you right clicked a button!!! :)")

    def SetDown(self):
      if self.down:
        self.downCommand()
        return
      self.down = True
      self.OnDownCommand()  

    def SetUp(self):
      if not self.down:
        return    
      self.down = False
      self.OnUpCommand()

    def draw(self):
        if self.down:
            gfxdraw.aacircle(screen, self.pos[0]+self.offSetPos[0], self.pos[1]+self.offSetPos[1], self.radius, self.down_color)
            gfxdraw.filled_circle(screen, self.pos[0]+self.offSetPos[0], self.pos[1]+self.offSetPos[1], self.radius, self.down_color)
        elif self.idle:
            gfxdraw.aacircle(screen, self.pos[0]+self.offSetPos[0], self.pos[1]+self.offSetPos[1], self.radius+1, self.idle_color)
            gfxdraw.filled_circle(screen, self.pos[0]+self.offSetPos[0], self.pos[1]+self.offSetPos[1], self.radius+1, self.idle_color)
        else:
            gfxdraw.aacircle(screen, self.pos[0]+self.offSetPos[0], self.pos[1]+self.offSetPos[1], self.radius, self.up_color)
            gfxdraw.filled_circle(screen, self.pos[0]+self.offSetPos[0], self.pos[1]+self.offSetPos[1], self.radius, self.up_color)
        if self.text:
            screen.blit(self.text,(self.pos[0]+self.textx+self.offSetPos[0],self.pos[1]+self.texty+self.offSetPos[1]))

    def update(self,things):
      mpos,mb1,mb3,keyQueue = things
      if self.key in keyQueue and ((not inputBoxSelected) or self.key in keysThatIgnoreBoxSelected):
        self.__dict__[self.keyCommand]()
      if sqrt((mpos[0]-self.pos[0]-self.offSetPos[0])**2+(mpos[1]-self.pos[1]-self.offSetPos[1])**2) > self.radius:
        self.idle = False
      else:
        self.idle = True
        if mb1:
          self.SetDown()
        else:
          self.SetUp()
        if self.accepts_mb3:
          if mb3:
            self.rightClickCommand()  

class ButtonSwitch:
  @classmethod
  def accepts(cls) -> tuple:
    return ('mpos','mb1down')

  def __init__(self,pos,size,start_state,state_pics,big_hitbox:bool = False):
    self.pos = pos
    self.size = size
    self.state = start_state
    self.state_pics = state_pics

  def update(self,things):
    mpos,mb1 = things
    if mpos[0] > self.pos[0] and mpos[0] < self.pos[0] + self.size[0]:
      if mpos[1] > self.pos[1] and mpos[1] < self.pos[1] + self.size[1]:  
        if mb1:
          self.state = (self.state + 1) % len(self.state_pics)

  def draw(self):
    screen.blit(self.state_pics[self.state],self.pos)
  
class CheckBox:
  @classmethod
  def accepts(cls) -> tuple:
    return ('mpos','mb1down')
  __slots__ = ('pos','size','func','_rect','_offSetPos','box_color','font','txt','tpos','_selected','onlyOn')
  def __init__(self,pos:tuple,size:number,func:Callable,box_color:tuple = (110,110,110),txt:str = '',font = None,tpos = (20,0),onlyOn:bool = False) -> None:
    self.onlyOn = onlyOn
    self.pos = pos
    self.size = (size,size)
    self.func = func
    self._rect = Rect(pos,self.size)
    self._offSetPos = (0,0)
    self.selected = False
    self.box_color = box_color
    if txt:
      self.font = font
      if self.font is None:
        self.font = makeFont('Arial',size)
      self.txt = self.font.render(txt,True,(0,0,0))
    else:
      self.txt = None
    self.tpos = tpos
    

  @property
  def selected(self) -> bool:
    raise Warning('Should use instead <CheckBox>._selected')
    return self._selected
  
  @selected.setter
  def selected(self,newVal:bool) -> None:
    self._selected = newVal
    if self.onlyOn:
      if newVal:
        self.func(newVal)
    else:
      self.func(newVal)
  @property
  def offSetPos(self) -> tuple:
    raise Warning('Should use instead <CheckBox>._offSetPos')
    return self._offSetPos
  
  @offSetPos.setter
  def offSetPos(self,newVal) -> None:
    self._offSetPos = newVal
    self._rect = Rect(self.pos[0]+self._offSetPos[0],self.pos[1]+self._offSetPos[1],self.size[0],self.size[1])


  def update(self,things) -> None:
    'mpos,mb1down'
    mpos, mb1d = things
    if mb1d and self._rect.collidepoint(mpos):
      if self.onlyOn:
        if not self._selected:
          self.selected = not self._selected
      else:
        self.selected = not self._selected
      

  def draw(self) -> None:
    draw.rect(screen,self.box_color,self._rect,(not self._selected)*3,3)
    if self.txt is not None:
      screen.blit(self.txt,(self.pos[0]+self._offSetPos[0]+self.tpos[0],self.pos[1]+self._offSetPos[1]+self.tpos[1]))
    

class KeyBoundFunction:
  @classmethod
  def accepts(cls) -> tuple:
    return ('KDQueue',)
  
  __slots__ = ('func','keys','offSetPos')
  def __init__(self,func:Callable,*keys):
    self.func = func
    self.keys = set(keys)

  def update(self,things) -> None:
    '''KDQueue'''
    KDQueue = set(things[0])
    #find all keys that we accept, if list is empty return
    #else if inputboxselected then check if keys that ignore 
    KDQueue.intersection_update(self.keys)
    if inputBoxSelected:
      KDQueue.intersection_update(keysThatIgnoreBoxSelected)
    if KDQueue:
      self.func()

  def draw(self) -> None:
    pass

class FPS(TextBox):
  '''Type of <TextBox> which will always display the current fps'''
  def __init__(self,pos):
    super().__init__(pos,makeFont('Arial',20,True),'',(255,255,255))
    self.last_time = time.perf_counter()
  def update(self,things):
    this_time = time.perf_counter()
    self.setText(f'{(1/(this_time-self.last_time)).__trunc__()}')
    self.last_time = this_time

class OnScroll:
  @classmethod
  def accepts(cls) -> tuple:
    return 'wheel',

  def __init__(self,command):
    self.cmd = command

  def update(self,things):
    #we know that things[0] is the wheel 
    if things[0]:
      self.cmd(things[0])
    
  def draw(self):
    pass

class Button:
  font.init()
  default_font = font.SysFont("Arial",20)
  @classmethod
  def accepts(cls) -> tuple:
    return ('mpos','mb1down','mb3down','KDQueue','mb1up')
  #__slots__ = ('x','y','xlen','ylen','OnDownCommand','OnUpCommand','down_color','up_color','down','previous_state','idle_color','text','textx','texty','idle','state','key','text_color','accepts_mb3','rightClickCommand','keyCommand','_offSetPos','_offsetY','_rect','pidle')
  def __init__(self,pos,xlen,ylen,OnDownCommand,down_color,up_color,idle_color,text:Surface|str = Surface((0,0)),textx:int = 0,texty:int = 0,rightClickCommand:Callable|None = None,key:str|None = None,accepts_mb3:bool = False, OnUpCommand:Callable|None = None,keyCommand:str = 'OnDownCommand',text_color:tuple = (0,0,0)):
    self.x = pos[0]
    self.y = pos[1]
    self.xlen = xlen
    self.ylen = ylen
    self.OnDownCommand = OnDownCommand
    self.OnUpCommand = OnUpCommand if OnUpCommand else lambda:0
    self.down_color = down_color
    self.up_color = up_color
    self.down = False
    self.previous_state = False
    self.idle_color = idle_color
    self.text_color = text_color
    if isinstance(text,str):
      self.text = self.default_font.render(text,True,self.text_color)
    else:
      self.text = text
    self.textx = textx
    self.texty = texty
    self.idle = False
    self.state = False
    self.key = key
    self.accepts_mb3 = accepts_mb3
    self.rightClickCommand = rightClickCommand if rightClickCommand is not None else lambda:None
    self.keyCommand = keyCommand
    self._offSetPos = (0,0)
    self._offsetY = 0
    self.offSetPos = (0,0)
    self.offsetY = 0
    self.pidle = 0
    self._rect = Rect(self.x,self.y,self.xlen,self.ylen)
   
  @property
  def offSetPos(self):
    return self._offSetPos
  
  @property
  def offsetY(self):
    return self._offsetY
  
  @offsetY.setter
  def offsetY(self,newVal):
    self._offsetY = newVal
    self._rect = Rect(self.x+self.offSetPos[0],self.y+self.offSetPos[1]-self.offsetY,self.xlen,self.ylen)
    self.textpos = (self.x+self.textx + self.offSetPos[0],self.y + self.texty + self.offSetPos[1] - newVal)

  @offSetPos.setter
  def offSetPos(self,newVal):
    self._offSetPos = newVal
    self._rect = Rect(self.x+newVal[0],self.y+newVal[1]-self.offsetY,self.xlen,self.ylen)
    self.textpos = (self.x+self.textx + self._offSetPos[0],self.y + self.texty + self._offSetPos[1] - self._offsetY)
  def onMouseEnter(self):
    #function to be overwritten for extra functionality
    pass
  def onMouseExit(self):
    #function to be overwritten for extra functionality
    pass

  def draw(self) -> None:
    global screen
    if self.down:
      draw.rect(screen, self.down_color, self._rect)
    elif self.idle:
      draw.rect(screen, self.idle_color, self._rect)
    else:
      draw.rect(screen, self.up_color, self._rect)
    screen.blit(self.text,self.textpos)  
  def setToUp(self) -> None:
    self.idle = False
    self.down = False

  def update(self,things) -> None:
    '''mpos,mb1down,mb3down,KDQueue,mb1up'''
    mpos,mb1down, mb3,keyQueue,mb1up = things

    if keyQueue and self.key:
      if self.key in keyQueue and ((not inputBoxSelected) or self.key in keysThatIgnoreBoxSelected):
        self.__dict__[self.keyCommand]()
    if self._rect.collidepoint(mpos):
      if not self.pidle:
        self.onMouseEnter()
      self.idle = True
      if mb1down:
        self.OnDownCommand()
        self.down = True
      elif self.down and mb1up: #if we are down and just released mouse
        self.OnUpCommand()
        self.down = False

      if self.accepts_mb3 and mb3:
        self.rightClickCommand()
    elif self.pidle:
      self.idle = False
      self.down = False
      self.onMouseExit()
    self.pidle = self.idle

class MiniWindow:
  def __init__(self,name,pos,size,color =(70,70,70),exit_command:Callable = lambda:1,force_focus:bool = True):
    self._offset = tuple(pos)
    self._size = tuple(size)
    if self._size[1] < 100: raise TypeError("Cannot Make A MiniWindow that small")
    self._background_color = color
    self._rect = Rect(self._offset[0],self._offset[1],self._size[0],self._size[1])
    self._top_rect = Rect(self._offset[0],self._offset[1],self._size[0],25) 
    self._force_focus = force_focus
    self._mpos = (0,0)
    self._pmpos = (0,0)
    self.window_caption = TextBox((5,5),font.SysFont('Arial',15),name,(0,0,0))
    self.onStart = lambda:None
    self.exit_button = Button((size[0]-30,0),30,25,lambda:1,(255,100,100),(210,210,210),(255,10,10),'',7,4,OnUpCommand=exit_command)

  def __setattr__(self, __name: str, __value) -> None:
    if __name not in {'_offset','_background_color','_size','_rect','_top_rect','_force_focus','_pmpos','_mpos','onStart'}:
      self.__dict__[__name] = __value
      self.__dict__[__name].offSetPos = self._offset
    else:
      self.__dict__[__name] = __value


  def ChangeObjsOffset(self,newOffset,newSize) -> None:
    self._offset = tuple(newOffset)
    self._size = tuple(newSize)
    for obj in self.__dict__:
      if obj not in {'_offset','_background_color','_size','_rect','_top_rect','_force_focus','_pmpos','_mpos','onStart'}:
        self.__dict__[obj].offSetPos = tuple(newOffset)
    self._rect = Rect(self._offset[0],self._offset[1],self._size[0],self._size[1])

  def move(self,newOffset):
    self._offset = (self._offset[0]+ newOffset[0],self._offset[1]+newOffset[1])
    for obj in self.__dict__:
      if obj not in {'_offset','_background_color','_size','_rect','_top_rect','_force_focus','_pmpos','_mpos','onStart'}:
        self.__dict__[obj].offSetPos = self._offset
    self._rect.move_ip(newOffset)
    self._top_rect.move_ip(newOffset)

  def update(self,myInput:Input):
    if not self._force_focus:
      self._mpos = myInput.mpos
      if self._top_rect.collidepoint(self._mpos) or self._top_rect.collidepoint(self._pmpos):
        if myInput.mb1:
          self.move((self._mpos[0]-self._pmpos[0],self._mpos[1]-self._pmpos[1]))
      self._pmpos = self._mpos

    for object in self.__dict__:
      if object not in {'_offset','_background_color','_size','_rect','_top_rect','_force_focus','_pmpos','_mpos','onStart'}:
        #objInput = [myInput.__getattr__(acceptableInput) for acceptableInput in self.__dict__[object].accepts()]
        self.__dict__[object].update(myInput.get_all(self.__dict__[object].accepts()))

  def draw(self):
    draw.rect(screen,self._background_color,self._rect)
    draw.rect(screen,(210,210,210),self._top_rect)
    top_x = (self._offset[0]+self._size[0]-23)
    top_y = (self._offset[1]+5)
    bottom_x = (self._offset[0]+self._size[0]-8)
    bottom_y = (self._offset[1]+20)
    for drawThing in self.__dict__:
      if drawThing not in ('_offset','_background_color','_size','_rect','_top_rect','_force_focus','_pmpos','_mpos','onStart'):
        self.__dict__[drawThing].draw()
    draw.line(screen,(0,0,0),(top_x,top_y),(bottom_x,bottom_y),2)
    draw.line(screen,(0,0,0),(top_x,bottom_y),(bottom_x,top_y),2)
    

class Empty:
  @classmethod
  def accepts(cls) -> tuple:
    return ()
  def __init__(self):
    pass

  def update(self,_):
    pass

  def draw(self,_):
    pass

class Stopwatch:
  def __init__(self,function = time.time):
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

  def stop(self):
    time = self.timeElapsed()
    self.paused = 0
    self.startTime = None
    self.extraTime = 0
    return time

  def timeElapsed(self):
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



##########################
class Main_Space:
    @classmethod
    def accepts(cls) -> tuple:
      return ()
    def __init__(self):
        pass

    def update(self,*_):
        pass

    def draw(self,*_):
        pass
    
    def onQuit(self):
        pass

class Border:
    _draw_need:int
    _rect:Rect
    def __init__(self):
        pass

    def update(self):
        pass

    def draw(self):
        pass

class Window_Space:
    #TODO optimize the draw method for MS and borders so that in the first_update they get a list of what everything they need to do and then they store it to not call <obj>.accepts() each frame
    '''def __new__(cls): 
      if not hasattr(cls, 'instance'):
        cls.instance = super(Window_Space, cls).__new__(cls)
      return cls.instance'''
    def __init__(self):
      self._background_color = (0,0,0)
      self._mainSpaces = []
      self._mainSpace = None
      self._activeMainSpace = 0
      self._mainSpacePos = [0,0]
      self._mainSpaceSize = [WIDTH,HEIGHT]
      self._borders:dict[str,None|Border] = {"top":None,"bottom":None,"left":None,"right":None}  
      self._miniWindows = {}     
      self._debug = Main_Space()
      self._miniwindowactive = False
      self._drawRects = []
      self._rect = Rect(0,0,WIDTH,HEIGHT)
      self._msRect = self._rect
      self._mpos = (0,0)
      self._pmpos = (0,0)
      self._activeMiniWindow:MiniWindow
      
  

    def addMiniWindow(self,name:str,pos:tuple,size:tuple,bg_color=None,exit_command:Callable|None=None,force_focus:bool = True) -> None:
      if bg_color == None:
        bg_color = (70,70,70)
      if exit_command == None:
        exit_command = self.deactivateMiniWindow
      self._miniWindows[name] = MiniWindow(name,pos,size,bg_color,exit_command,force_focus)
    def activateMiniWindow(self,name,passFunc:bool = False) -> None|Callable:
      if passFunc: return lambda :self.activateMiniWindow(name)
      assert name in self._miniWindows.keys(), "That miniwindow does not exist"
      #if not name in self._miniWindows.keys(): raise TypeError('That miniwindow does not exist')
      if self._activeMiniWindow is not self._miniWindows[name]:
        assert not self._miniwindowactive, 'Only one MiniWindow can be active at a time'
      #if self._miniwindowactive: raise TypeError('Only one MiniWindow can be active at a time')
      self.miniWindow(name).onStart()
      self._miniwindowactive = True
      self._activeMiniWindow = self._miniWindows[name]
    def deactivateMiniWindow(self) -> None:
      self._miniwindowactive = False
      self._activeMiniWindow = None #type: ignore
      self._currentMS = self.mainSpace
      self.first_draw()
    def miniWindow(self,name) -> MiniWindow:
      return self._miniWindows[name]
    @property
    def top(self) -> Border|None: return self._borders['top']
    @property
    def left(self) -> Border|None: return self._borders['left']
    @property
    def right(self) -> Border|None: return self._borders['right']
    @property 
    def bottom(self) -> Border|None: return self._borders['bottom']
    @property
    def mainSpace(self):
      t = self._mainSpaces[self._activeMainSpace]
      assert isinstance(t,ScrollingMS)
      return t
    @property
    def MSSize(self) -> tuple:
      return self._mainSpaceSize
    @property
    def MSPos(self) -> tuple:
      return self._mainSpacePos
    def drawBorder(self,borderName):
      assert borderName in self._borders.keys(), f'Border named :{borderName} does not exist'
      border = self._borders[borderName]
      border.draw()

    @property
    def activeMainSpace(self) -> int:
      return self._activeMainSpace
    
    def getMainSpace(self,num:int) -> Main_Space:
      return self._mainSpaces[num]
    
    def drawMS(self) -> None:
      '''Draw Active Main Space'''
      self._mainSpaces[self._activeMainSpace].draw()
    
    def deleteMainSpace(self,num:int) -> None:
      del self._mainSpaces[num]
      if self._activeMainSpace == len(self._mainSpaces):
        self._activeMainSpace -= 1
        self._currentMS = self._mainSpaces[self._activeMainSpace]
        self._currentMS.draw()
        
    @property
    def leftSize(self) -> int:
      try:
        return self._borders['left']._size[0]
      except AttributeError:
        return 0
    @property
    def topSize(self) -> int:
      try:
        return self._borders['top']._size[1]
      except AttributeError:
        return 0
    @property
    def rightSize(self) -> int:
      try:
        return self._borders['right']._size[0]
      except AttributeError:
        return 0
    @property
    def bottomSize(self) -> int:
      try:
        return self._borders['bottom']._size[1]
      except AttributeError:
        return 0 
    @mainSpace.setter
    def mainSpace(self, newVal:int | Main_Space) -> None:
      if isinstance(newVal,int):
        self._activeMainSpace = newVal
        self._currentMS = self._mainSpaces[newVal]
      elif isinstance(newVal,ScrollingMS):
        self._mainSpaces.append(newVal)
        self._activeMainSpace = len(self._mainSpaces)-1
        self._currentMS = self._mainSpaces[-1]
      else:
        return
      self._update_mainspace()
      #self._currentMS.draw()
      #display.update(self._msRect)

    def addMainSpace(self,newMS:Main_Space) -> None:
      self._mainSpaces.append(newMS)
      self._update_mainspace()

    def addDebugInfo(self,impact:int = 30) -> None:
      '''impact is how much you want the debug impact the current performance.
      the lower 'impact' is the higher the actual impact, impact > 0'''
      self._debug = Debug(performanceImpact=impact)
    
    def setActiveMainSpace(self,newVal:int) -> None:
      self._activeMainSpace = newVal
      self._currentMS = self._mainSpaces[newVal]
      self._currentMS.draw()
    
    def emptyMainSpace(self,num:int) -> None:
      for var in self._mainSpaces[num].__dict__:
        if var not in self._mainSpaces[num]._defaults:
          del self._mainSpaces[num].__dict__[var]

    @property
    def background_color(self) -> tuple:
      return self._background_color

    @background_color.setter
    def background_color(self,newColor) -> None:
      if not isinstance(newColor,tuple):
        raise TypeError("Has to be a tuple!")
      if len(newColor) != 3:
        raise TypeError("Color assignment is (R,G,B) (no A)!")
      for color in newColor:
        if not (0<= color <= 255):
          raise TypeError("Color range is not within bounds!")
      self._background_color = newColor

    def addBorder(self,direction:str,sizeintoMid,color,draw_need = 1,border_border_color:tuple = (0,0,0),border_border_width:int = 0) -> None:
      if direction == 'top':
        self._borders['top'] = Top_Border(color,draw_need,border_border_color,border_border_width)
        self._borders['top'].setSizeAndPos(self._borders,sizeintoMid)
        self._mainSpacePos[1] = sizeintoMid
        self._mainSpaceSize[1] -= sizeintoMid
        self._update_mainspace()
      elif direction == 'bottom':
        self._borders['bottom'] = Bottom_Border(color,draw_need,border_border_color,border_border_width)
        self._borders['bottom'].setSizeAndPos(self._borders,sizeintoMid)
        self._mainSpaceSize[1] -= sizeintoMid
        self._update_mainspace()
      elif direction == 'left':
        self._borders['left'] = Left_Border(color,draw_need,border_border_color,border_border_width)
        self._borders['left'].setSizeAndPos(self._borders,sizeintoMid)
        self._mainSpacePos[0] = sizeintoMid
        self._mainSpaceSize[0] -= sizeintoMid
        self._update_mainspace()
      elif direction == 'right':
        self._borders['right'] = Right_Border(color,draw_need,border_border_color,border_border_width)
        self._borders['right'].setSizeAndPos(self._borders,sizeintoMid)
        self._mainSpaceSize[0] -= sizeintoMid
        self._update_mainspace()

    def update_mainspace(self,num) -> None:
      '''draw specific mainspace'''
      self._mainSpaces[num].draw()

    def _update_mainspace(self) -> None:
      self._msRect = Rect(self._mainSpacePos[0],self._mainSpacePos[1],self._mainSpaceSize[0],self._mainSpaceSize[1])
      for mainSpace in self._mainSpaces:
        mainSpace.ChangeObjsOffset(self._mainSpacePos,self._mainSpaceSize)
        
    def initiate(self):
      self.first_update()
      self.first_draw()

    def first_update(self) -> None:
      self._live_borders = tuple([x for x in self._borders.values() if x != None])

    def update(self,input:Input) -> None:
      self._mpos = input.mpos
      if not self._miniwindowactive:
        self.mainSpace.update(input)
        for border in self._live_borders: #type: ignore
          border:Top_Border #just an example to help autocorrect
          border.update(input)

      elif not self._activeMiniWindow._force_focus:  #miniwindow active, but not forced focus 
        if self._activeMiniWindow._rect.collidepoint(self._mpos) or self._activeMiniWindow._rect.collidepoint(self._pmpos):
          self._activeMiniWindow.update(input)
        else:
          self.mainSpace.update(input)
          for border in self._live_borders: #type: ignore
            border:Top_Border #just an example to help autocorrect
            border.update(input)
      else:
        self._activeMiniWindow.update(input)
      self._pmpos = self._mpos
      self._debug.update()


    def first_draw(self) -> None:
      self.mainSpace.draw()
      for border in self._borders.values():
        if border != None:
          border.draw()
      
      #arrange borders by draw_need so that self.draw() can draw them
      self._draw_when_needed_borders = tuple([border for border in self._borders.values() if border != None and border._draw_need == 1])
      self._need_to_draw_borders =  tuple([border for border in self._borders.values() if border != None and border._draw_need == 2])

    def draw(self) -> None:
      if not self._miniwindowactive:   
        screen.fill(self.background_color)
        self._currentMS:ScrollingMS
        if self._currentMS._draw_need == 1 and self._msRect.collidepoint(self._mpos):
          self._currentMS.draw()
        else:
          for border in self._draw_when_needed_borders:
            if border._rect.collidepoint(self._mpos):
              border.draw()
              break #break cause further checking is useless cause we know that mpos can only collide with one rect
        if self._currentMS._draw_need == 2:
          self._currentMS.draw()
        for border in self._need_to_draw_borders:
          border.draw()

      elif not self._activeMiniWindow._force_focus:
        screen.fill(self.background_color)
        self._currentMS.draw()
        for border in self._live_borders:
          border.draw()
        self._activeMiniWindow.draw()

      else: 
        self._activeMiniWindow.draw()
      self._debug.draw()      

    def onQuit(self) -> None:
      self._debug.onQuit()

class Top_Border(Border):
    def __init__(self,color,draw_need,border_color:tuple = (0,0,0),border_width:int = 0):
      self._color = color
      self._pos:tuple
      self._size:tuple
      self._rect:Rect
      self._draw_need = draw_need
      self._active = 0
      self._pactive = 0
      self._border_color = border_color
      self._border_width = border_width
      self._border_exists = 1 if border_width else 0

    def __setattr__(self, __name: str, __value) -> None:
      if __name[0] == '_':
        self.__dict__[__name] = __value
      else:
        self.__dict__[__name] = __value
        self.__dict__[__name].offSetPos = self._pos

    def setSizeAndPos(self, existingBorders:dict,ylen):
      if existingBorders['left'] == None:
        self._pos = (0,0) 
      else:
        self._pos = (existingBorders['left']._size[0],0)
      if existingBorders['right'] == None:
        self._size = (WIDTH-self._pos[0],ylen)
      else:
        self._size = (WIDTH-self._pos[0]-existingBorders['right']._size[0],ylen)
      self._rect = Rect(self._pos[0],self._pos[1],self._size[0],self._size[1])

    def onMouseEnter(self):
      pass
    def onMouseExit(self):
      pass

    def update(self,myInput:Input):
      if self._rect.collidepoint(myInput.mpos):
        self._active = 1
      else:
        self._active = 0
      if self._active and not self._pactive:
        self.onMouseEnter()
      elif not self._active and self._pactive:
        draw.rect(screen,self._color,self._rect)
        self.onMouseExit()
        if not self._draw_need: return
        for object in self.__dict__:
          if object[0] != '_':
            obj = self.__dict__[object]
            if isinstance(obj,Button):
              obj.setToUp()
            obj.draw()
        if self._border_exists:
          draw.rect(screen,self._border_color,self._rect,self._border_width)
      for object in self.__dict__:
        if object[0] != '_':
          #objInput = [myInput.__getattr__(acceptableInput) for acceptableInput in self.__dict__[object].accepts()]
          self.__dict__[object].update(myInput.get_all(self.__dict__[object].accepts()))
      self._pactive = self._active

    def draw(self):
      draw.rect(screen,self._color,self._rect)
      for object in self.__dict__:
        if object[0] != '_':
          self.__dict__[object].draw()
      if self._border_exists:
        draw.rect(screen,self._border_color,self._rect,self._border_width)

class Left_Border(Border):
    def __init__(self,color,draw_need,border_color:tuple = (0,0,0),border_width:int = 0):
      self._pos = (0,0)
      self._color = color
      self._draw_need = draw_need
      self._active = 0
      self._pactive = 0
      self._border_color = border_color
      self._border_width = border_width
      self._border_exists = 1 if border_width else 0

    def __setattr__(self, __name: str, __value) -> None:
      if __name[0] != '_':
        self.__dict__[__name] = __value
        self.__dict__[__name].offSetPos = self._pos
      else:
        self.__dict__[__name] = __value

    def onMouseEnter(self):
      pass
    def onMouseExit(self):
      pass
    def setSizeAndPos(self, existingBorders:dict,xlen):
      if existingBorders['top'] == None:
        self._pos = (0,0)
      else:
        self._pos = (0,existingBorders['top']._size[1])
      if existingBorders['bottom'] == None:
        self._size = (xlen,HEIGHT-self._pos[1])
      else:
        self._size = (xlen,HEIGHT-self._pos[1]-existingBorders['bottom']._size[1])
      self._rect = Rect(self._pos[0],self._pos[1],self._size[0],self._size[1])

    def update(self,myInput:Input):
      if self._rect.collidepoint(myInput.mpos):
        self._active = 1
      else:
        self._active = 0
      if self._active and not self._pactive:
        self.onMouseEnter()
      elif not self._active and self._pactive:
        self.onMouseExit()
        if not self._draw_need: return
        draw.rect(screen,self._color,self._rect)
        for object in self.__dict__:
          if object[0] != '_':
            obj = self.__dict__[object]
            if isinstance(obj,Button):
              obj.setToUp()
              obj.draw()
            elif isinstance(obj,Dropdown):
              obj.setAllToUp()
              obj.draw()
            else:
              obj.draw()
        if self._border_exists:
          draw.rect(screen,self._border_color,self._rect,self._border_width)
      for object in self.__dict__:
        if object[0] != '_':
          #objInput = [myInput.__getattr__(acceptableInput) for acceptableInput in self.__dict__[object].accepts()]
          self.__dict__[object].update(myInput.get_all(self.__dict__[object].accepts()))
      self._pactive = self._active

    def draw(self):
      draw.rect(screen,self._color,self._rect)
      for obj in self.__dict__:
        if obj[0] != '_':
          self.__dict__[obj].draw()
      if self._border_exists:
        draw.rect(screen,self._border_color,self._rect,self._border_width)

class Right_Border(Border):
    def __init__(self,color,draw_need,border_color:tuple = (0,0,0),border_width:int = 0):
      self._color = color
      self._pos: tuple
      self._size: tuple
      self._rect: Rect
      self._draw_need = draw_need
      self._active = 0
      self._pactive = 0
      self._border_color = border_color
      self._border_width = border_width
      self._border_exists = 1 if border_width else 0

    def __setattr__(self, __name: str, __value) -> None:
      if __name[0] == '_':
        self.__dict__[__name] = __value
      else:
        self.__dict__[__name] = __value
        self.__dict__[__name].offSetPos = self._pos

    def setSizeAndPos(self, existingBorders:dict,xlen):
      if existingBorders['top'] == None:
        self._pos = (WIDTH-xlen,0) 
      else:
        self._pos = (WIDTH-xlen,existingBorders['top']._size[1])
      if existingBorders['bottom'] == None:
        self._size = (WIDTH-self._pos[0],HEIGHT-self._pos[1])
      else:
        self._size = (WIDTH-self._pos[0],HEIGHT-self._pos[1]-existingBorders['bottom']._size[1])
      self._rect = Rect(self._pos[0],self._pos[1],self._size[0],self._size[1])

    def onMouseEnter(self):
      pass
    def onMouseExit(self):
      pass

    def update(self,myInput:Input):
      if self._rect.collidepoint(myInput.mpos):
        self._active = 1
      else:
        self._active = 0
      if self._active and not self._pactive:
        self.onMouseEnter()
      elif not self._active and self._pactive:
        draw.rect(screen,self._color,self._rect)
        self.onMouseExit()
        if not self._draw_need: return
        for object in self.__dict__:
          if object[0] != '_':
            obj = self.__dict__[object]
            if isinstance(obj,Button):
              obj.setToUp()
            obj.draw()
        if self._border_exists:
          draw.rect(screen,self._border_color,self._rect,self._border_width)
      for object in self.__dict__:
        if object[0] != '_':
          #objInput = [myInput.__getattr__(acceptableInput) for acceptableInput in self.__dict__[object].accepts()]
          self.__dict__[object].update(myInput.get_all(self.__dict__[object].accepts()))
      self._pactive = self._active

    def draw(self):
      draw.rect(screen,self._color,self._rect)
      for object in self.__dict__:
        if object[0] != '_':
          self.__dict__[object].draw()
      if self._border_exists:
        draw.rect(screen,self._border_color,self._rect,self._border_width)

class Bottom_Border(Border):
    def __init__(self,color,draw_need,border_color:tuple = (0,0,0),border_width:int = 0):
      self._pos = (0,0)
      self._size = (0,0)
      self._color = color
      self._draw_need = draw_need
      self._active = 0
      self._pactive = 0
      self._border_color = border_color
      self._border_width = border_width
      self._border_exists = 1 if border_width else 0

    def __setattr__(self, __name: str, __value) -> None:
      if __name[0] == '_':
        self.__dict__[__name] = __value
      else:
        self.__dict__[__name] = __value
        self.__dict__[__name].offSetPos = self._pos

    def setSizeAndPos(self, existingBorders:dict,ylen):
      if existingBorders['left'] == None:
        self._pos = (0,HEIGHT-ylen) 
      else:
        self._pos = (existingBorders['left']._size[0],HEIGHT-ylen)
      if existingBorders['right'] == None:
        self._size = (WIDTH-self._pos[0],ylen)
      else:
        self._size = (WIDTH-self._pos[0]-existingBorders['right']._size[0],ylen)
      self._rect = Rect(self._pos[0],self._pos[1],self._size[0],self._size[1])
    
    def onMouseEnter(self):
      pass
    def onMouseExit(self):
      pass

    def update(self,myInput:Input):
      if self._rect.collidepoint(myInput.mpos):
        self._active = 1
      else:
        self._active = 0
      if self._active and not self._pactive:
        self.onMouseEnter()
      elif not self._active and self._pactive:
        self.onMouseExit()
        if not self._draw_need: return
        for object in self.__dict__:
          if object[0] != '_':
            obj = self.__dict__[object]
            if isinstance(obj,Button):
              obj.setToUp()
              obj.draw()
        if self._border_exists:
          draw.rect(screen,self._border_color,self._rect,self._border_width)
      for object in self.__dict__:
        if object[0] != '_':
          #objInput = [myInput.__getattr__(acceptableInput) for acceptableInput in self.__dict__[object].accepts()]
          self.__dict__[object].update(myInput.get_all(self.__dict__[object].accepts()))
      self._pactive = self._active
    def draw(self):
      draw.rect(screen,self._color,self._rect)
      for object in self.__dict__:
        if object[0] != '_':
          self.__dict__[object].draw()
      if self._border_exists:
        draw.rect(screen,self._border_color,self._rect,self._border_width)

class ScrollingMS(Main_Space):
    def __init__(self,draw_need = 2,update_need = 1):
      #update need explained: 0 = only update when mpos on self, 1 = always update when update method called
      #draw need explained: 0 -> dont draw, 1 => only draw when touching mouse, 2 => always draw 
      super().__init__()
      self._scrollVal = 0
      self._offset = (0,0)
      self._size = (WIDTH,HEIGHT)
      self._background_color = (0,0,0)
      self._rect = Rect(self._offset[0],self._offset[1],self._size[0],self._size[1])
      self._draw_need = draw_need
      self._defaults = {}
      self._active = 0
      self._pactive = 0
      self._update_need = update_need
      self._Screen_Objects = []
      self._Screen_Objects_accepts = []
      ###self._defaults setter should go last###
      self._defaults = {name for name in self.__dict__}

    @property
    def size(self):
      return self._size

    @property
    def background_color(self):
      self._background_color
    
    @background_color.setter
    def background_color(self,newVal) -> None:
      self.set_background_color(newVal)

    def set_background_color(self,newColor):
      if not isinstance(newColor,tuple):
        raise TypeError("Has to be a tuple!")
      if len(newColor) != 3:
        raise TypeError("Color assignment is (R,G,B) (no A)!")
      for color in newColor:
        if not (0<= color <= 255):
          raise TypeError("Color range is not within bounds!")
      self._background_color = newColor

    def __setattr__(self, __name: str, __value) -> None:
      if __name[0] != '_' :
        self.__dict__[__name] = __value
        __value.offSetPos = self._offset
        self._Screen_Objects.append(__value)
        self._Screen_Objects_accepts.append(__value.accepts())
      else:
        self.__dict__[__name] = __value

    def onMouseEnter(self):
      pass
    def onMouseExit(self):
      pass
    def ChangeObjsOffset(self,newOffset,newSize) -> None:
      self._offset = tuple(newOffset)
      self._size = tuple(newSize)
      for obj in self.__dict__:
        if obj not in self._defaults:
          self.__dict__[obj].offSetPos = tuple(newOffset)
      self._rect = Rect(self._offset[0],self._offset[1],self._size[0],self._size[1])

    def update(self,myInput:Input):
      if self._rect.collidepoint(myInput.mpos):
        self._active = 1
      else:
        self._active = 0
      if self._active and not self._pactive:
        self.onMouseEnter()
      elif not self._active and self._pactive:
        self.onMouseExit()
        for obj in self.__dict__.values():
          if isinstance(obj,Button):
            obj.setToUp()
          elif isinstance(obj,Dropdown):
            obj.setAllToUp()
        if self._draw_need == 1:
          self.draw()
      if not self._active and not self._update_need: return
      #for object in self.__dict__:
      #  if object not in self._defaults:
      #    objInput = [myInput.__getattr__(acceptableInput) for acceptableInput in self.__dict__[object].accepts()]
      #    self.__dict__[object].update(objInput)
      for object,accepts in zip(self._Screen_Objects,self._Screen_Objects_accepts):
        accepts:list
        object:Empty #can be any Screen Object.
        object.update(myInput.get_all(accepts))
      self._pactive = self._active

    def draw(self):
      draw.rect(screen,self._background_color,self._rect)
      for obj in self._Screen_Objects:
          obj.draw()
#print("BIG SAVINGS ON BEING ABLE TO PASS IN .accepts RETURN VALUE DIRECTLY INTO <Input> CLASS TO LOWER FUNC CALLS!!")
class SpaceMS(Main_Space):
    def __init__(self):
        super().__init__()
        self.spacePos = [0,0]
   
def log(_log:str):
  if not isinstance(_log,str):
    try:
      _log = str(_log)
    except:
      raise Exception(f'{_log}: type <{type(_log)}> could not be converted to string')
  with open(PATH+"/"+log_path,'a+') as file:
    file.write(_log+'\n')


def tick() -> int:
  global fps, dt 
  dt = clock.tick(fps)
  return dt

def get_screen_size() -> tuple[int,int]:
  return display.get_window_size()

def pre_init() -> None:
    '''Sets Variables _HEIGHT and _WIDTH'''
    global screenInfo, _WIDTH,_HEIGHT,preInitiated
    if not preInitiated:
      pginit()
      screenInfo = display.Info()
      _WIDTH,_HEIGHT = screenInfo.current_w,screenInfo.current_h
      del screenInfo
      preInitiated = 1

def radians_to_degrees(x:float):
  return x * 180 / pi

def iconify():
  '''Minimize screen'''
  display.iconify()

minimize = iconify

def init(screenSize:tuple,flags = 0,name:str = '',**kwargs) -> None:
  #nerf miner
  global saved_flags,saved_name,clock
  saved_flags = flags
  saved_name = name
  if not preInitiated:
    pre_init()
  global screen, running,WIDTH,HEIGHT
  if screenSize == (0,0):
    screenSize = (_WIDTH,_HEIGHT)
  screen = display.set_mode(screenSize,flags,**kwargs)
  scrap.init()
  WIDTH,HEIGHT = screenSize
  if name:
    display.set_caption(name)
  running = 1
  clock = pg_time.Clock()

def setSurface(surf:Surface):
  global screen,WIDTH,HEIGHT,clock
  pre_init()  
  WIDTH,HEIGHT = surf.get_size()
  screen = surf
  clock = pg_time.Clock()

def getSurface():
  global screen,WIDTH,HEIGHT,clock
  pre_init()  
  WIDTH,HEIGHT = get_screen_size()
  screen = display.get_surface()
  clock = pg_time.Clock()

def rename(name:str) -> None:
  display.set_caption(name)

def MinScreenSize(x:int,y:int) -> None:
  global minScreenX,minScreenY
  minScreenX = x
  minScreenY = y

def getFonts() -> list[str]:
  return font.get_fonts()

def makeFont(FontName,FontSize,Bold:bool = False,Italic:bool = False):
  return font.SysFont(FontName,FontSize,Bold,Italic)

def findAllFiles(ending:str,addedPath:str = '',strip:bool = True) -> list[str]:
    '''Find all files with a specific extension like .png or .txt'''
    from os import walk
    all_songs = []
    path = dirname(realpath(__file__)) 
    for _root, _dirs, files in walk(path+'/'+addedPath): 
        for file in files:
            if file.endswith(ending):
              if strip:
                all_songs.append(str('.'.join(file.split('.')[:-1])))
              else:
                all_songs.append(str(file))
    return all_songs

def loadSound(_FileName:str = '',usePath:bool = True) -> None:
  global currentSoundName
  FileName = '\\'.join([PATH,_FileName]) if usePath else _FileName
  mixer.music.unload()
  if _FileName:
    if _FileName.endswith('.ogg'):
      mixer.music.load(FileName)
      currentSoundName = _FileName[:-4]
    else:
      mixer.music.load(FileName+'.ogg')
      currentSoundName = _FileName
  else:
    currentSoundName = ''
  onSoundLoad()

def playSound(loops:int = 0,start:int = 0,fade_ms:int = 0) -> None:
  #utmily
  mixer.music.play(loops,start,fade_ms)
  onSoundPlay()

def stopSound() -> None:
  mixer.music.stop()

def pauseSound() -> None:
  mixer.music.paused = 1 #type: ignore
  mixer.music.pause()

def unpauseSound() -> None:
  mixer.music.paused = 0 #type: ignore
  mixer.music.unpause()

def PauseUnPauseSound() -> None:
  if mixer.music.paused: #type: ignore
    unpauseSound()
  elif not mixer.music.paused: #type: ignore
    pauseSound()
  else:
    raise IndexError(f"Value mixer.music.paused is not a bool instead it is a {type(mixer.music.paused)}: {mixer.music.paused}") #type: ignore

def SetSoundVolume(newVal:float) -> None:
  if not isinstance(newVal,float):
    raise TypeError(f"Volume is not correct data type! '{type(newVal)}")
  elif newVal > 1:
    newVal = 1
  elif newVal < 0:
    newVal = 0
  mixer.music.set_volume(newVal)

def setSoundPos(newPos:float) -> None:
  try:
    mixer.music.set_pos(newPos)
  except PygameEngineError:
    if mixer.music.get_busy():
      raise SoundError('Cannot Set Position of Sound currently')
    else:
      raise SoundError('Cannot Set position of sound currently, it looks like you dont have a sound loaded, maybe that is the problem')

def onSoundLoad():
  pass

def onSoundPlay():
  pass

def setOnSoundLoad(func:Callable) -> None:
  global onSoundLoad
  onSoundLoad = func

def setOnSoundPlay(func:Callable) -> None:
  global onSoundPlay
  onSoundPlay = func

def setSoundEndEvent(func:Callable):
  global endEventFunction
  endEventFunction = func

def endEventFunction():
  pass

def getSoundVolume() -> float:
  return mixer.music.get_volume()

def getSoundPos() -> int:
  return mixer.music.get_pos()

def getSoundPause() -> bool:
  return mixer.music.paused  #type: ignore

def setWindowIcon(surf:Surface) -> None:
  display.set_icon(surf)

def loadImg(FileName:str,useAlpha:bool = False,usePath:bool = True) -> Surface:
  '''Returns a pygame Surface of image provided with FileName\n
  Use Alpha for Images that should have a transparent background'''
  global PATH
  fullFilePath = '/'.join([PATH,FileName]) if usePath else FileName
  if useAlpha:
    return image.load(fullFilePath).convert_alpha()
  else:
    return image.load(fullFilePath).convert()

def flipSurface(surface:Surface,x:bool,y:bool) -> Surface:
  return transform.flip(surface,x,y) 

def resizeSurface(surface:Surface,newSize:tuple,dest_surf:Surface|None = None) -> Surface:
  if dest_surf == None:
    return transform.scale(surface,newSize)
  else:
    return transform.scale(surface,newSize,dest_surf)
  
def resizeSurfaceSmooth(surface:Surface,newSize:tuple,dest_surf:Surface|None = None) -> Surface:
  if dest_surf is None:
    return transform.smoothscale(surface,newSize)
  else:
    return transform.smoothscale(surface,newSize,dest_surf)

def rotateSurface(surface:Surface,angle:float) -> Surface:
  return transform.rotate(surface,angle)

def isValidScreenSize(screenSize:tuple) -> bool:
  global minScreenX,minScreenY
  if screenSize[0] < minScreenX:
    return False
  if screenSize[1] < minScreenY:
    return False
  return True

def get_clipboard(raw:bool = False) -> str | bytes|None:
  for _type in scrap.get_types():
    if SCRAP_TEXT in _type:
      if raw:
        return scrap.get(SCRAP_TEXT)
      else:
        s = scrap.get(SCRAP_TEXT)
        if s:
          return s.decode('utf-8')
        return s
  return ''
def resizeToBecomeValid(screenSize:tuple) -> tuple[int,int]:
  global minScreenX,minScreenY,WIDTH,HEIGHT
  WIDTH,HEIGHT = (max(screenSize[0],minScreenX),max(screenSize[1],minScreenY))
  return (WIDTH,HEIGHT)

def rawInput() -> list[events.Event]:
  return events.get()

set_allowed_events = events.set_allowed
get_blocked_events = events.get_blocked
set_blocked_events = events.set_blocked
events_wait = events.wait

def getAllInput() -> Input:
  """Returns MouseState and KeyDownQueue, if quit event triggered, returns tuple (False,False)"""
  keyDownQueue,keyUpQueue,mbd,mbu  = [],[],[0,0,0],[0,0,0]
  scrollDown,scrollUp = 0,0
  flagsRaised = []
  for event in events.get():
    if event.type == QUIT:
      return Input(False,False,False,False)
    elif event.type == KEYDOWN:
      keyDownQueue.append(event.unicode)
      if event.unicode == paste_unicode:
        for letter in get_clipboard(): #type: ignore
          keyDownQueue.append(letter)
    elif event.type == KEYUP:
      keyUpQueue.append(event.unicode)  
    elif event.type == MOUSEBUTTONDOWN:
      if event.button == 4:
        scrollDown = 1
      elif event.button == 5:
        scrollUp = 1
      elif event.button < 4:
        mbd[event.button-1] = 1
    elif event.type == MOUSEBUTTONUP:
      if event.button < 4: 
        mbu[event.button-1] = 1
    elif event.type == MUSIC_END:
      endEventFunction()
    elif event.type == VIDEORESIZE:
      global WIDTH,HEIGHT
      WIDTH,HEIGHT = display.get_window_size()
      if not isValidScreenSize((WIDTH,HEIGHT)):
        display.set_mode((resizeToBecomeValid((WIDTH,HEIGHT))),saved_flags)
    flagsRaised.append(event.type)
  return Input((mouse.get_pos(),mouse.get_pressed(),scrollUp-scrollDown,mbd,mbu),(keyDownQueue,keyUpQueue),flagsRaised,dt)
#hola lola

