'''
Framework for building Graphical User Interfaces for existing applications\n
This has been used to make:\n
Pixel Art Program\n
Gravity Sim\n
Music Player (similar to Spotify)\n
Notes Application (trashy)
'''

import time
import pygame
pygame.init()
from os import walk
from pygame import gfxdraw
from pygame import Surface
from pygame import font
from pygame import display
from pygame import image
from pygame import draw
from pygame import Rect
from pygame import constants as const
from pygame import scrap
from pygame import transform
from pygame.time import Clock
from . import advanced_color
from . import unicode_constants as u_const
from .events import Event
from .FrameworkTypes import *
from . import Input as Input_
from .Input import Input
from .Input import getInput
from pygame.display import get_window_size as getWindowSize
import sys

def binaryApproximate(searchFunc:Callable[[int],int|float],target:int|float,start:int,end:int):
  assert start <= end
  if start == end: return start
  mid = (end-start) //2 + start
  if mid == start:
    return min(end,start,key=lambda x: abs(target-searchFunc(x)))
  val = searchFunc(mid)
  if target > val:
    return binaryApproximate(searchFunc,target,mid,end)
  elif target < val:
    return binaryApproximate(searchFunc,target,start,mid)
  else:
    return mid

def toNone(*args):
  return None

if sys.platform == 'win32':
  def maximize_screen():
    from ctypes import windll
    HWND = display.get_wm_info()['window']
    windll.user32.ShowWindow(HWND, 3)

minScreenX,minScreenY = 0,0
WHEEL_SENSITIVITY = 7
MONITOR_WIDTH = display.Info().current_w
MONITOR_HEIGHT = display.Info().current_h
DOUBLE_CLICK_THRESHOLD = 0.5

def set_WHEEL_SENSITIVITY(i:int) -> None:
  global WHEEL_SENSITIVITY
  WHEEL_SENSITIVITY = i


class ObjectValue(Generic[T]):
  __slots__ = 'obj','obj_change_event'
  def __init__(self,obj:T) -> None:
    self.obj = obj
    self.obj_change_event:Event[[T]] = Event()

  def set(self,obj:T): 
    self.obj = obj
    self.obj_change_event.fire(obj)

  def get(self): 
    return self.obj

class ColorScheme:
  def __init__(self,r:int,g:int,b:int):
    self.r = r
    self.g = g
    self.b = b
    
  def getActive(self): return self.getDark(20)
  def getIdle(self): return self.getLight(20)
  def getInactive(self): return self.color

  @property
  def color(self):
    return self.r,self.g,self.b

  def mix(self,other:"ColorScheme"):
    return ColorScheme((self.r+other.r)//2,(self.g+other.g)//2,(self.b+other.b)//2)
  def getDark(self,amount:int):
    return advanced_color.darken(self.r,self.g,self.b,amount)
  def getLight(self,amount:int):
    return advanced_color.lighten(self.r,self.g,self.b,amount)
  def getComplementary(self):
    return advanced_color.getComplementary(self.r,self.g,self.b)

class CloseButtonColorScheme(ColorScheme):
  def __init__(self,exit_color:ColorType,background_color:ColorType) -> None:
    super().__init__(*exit_color)
    self.bg_color = background_color
    
  def getActive(self):
    return advanced_color.darken(*self.color,100)

  def getInactive(self):
    return self.bg_color
  
  def withBGColor(self,bg_color:ColorType):
    return CloseButtonColorScheme(self.color,bg_color)

class DrawBase:
  order_in_layer = 0

class ColorLayout:
  def __init__(self,foreground:ColorType,background:ColorType,tertiary:ColorType|None = None):
    self.foreground = foreground
    self.background = background
    self.tertiary = tertiary or background

class Image: 
  def __init__(self,pos:tuple[int,int],image:Surface):
    self.pos = pos
    self.image = image
    self.pos = pos

  def draw(self,surf:Surface):
    surf.blit(self.image,self.pos)  

class BackgroundColor:
  order_in_layer = -1
  def __init__(self,color:ColorType = (0,0,0)):
    self.color = color

  def draw(self,surf:Surface):
    surf.fill(self.color)

class ColorArea(DrawBase):
  def __init__(self,pos:tuple[int,int],size:tuple[int,int],color:ColorType = (0,0,0)):
    self.rect = Rect(pos,size)
    self.color = color
    self.fill_x = size[0]==0
    self.fill_y = size[1]==0

  def onResize(self,size:tuple[int,int]):
    if self.fill_x:
      self.rect.width = size[0]
    if self.fill_y:
      self.rect.height = size[1]

  def draw(self,surf:Surface):
    surf.fill(self.color,self.rect)

class ButtonSwitch(DrawBase):
  def __init__(self,pos:tuple[int,int],size:tuple[int,int],states:list[Surface],state:int = 0,onDown:EventHookInt|None = None):
    self.rect = Rect(pos,size)
    self.states = states
    self.state = state
    self.onDown = onDown
    self.rect_color:Optional[ColorType] = None

  def update(self,input:Input):
    if input.mb1d and self.rect.collidepoint(input.mpos):
      self.state = (self.state + 1) % len(self.states)
      if self.onDown:
        self.onDown(self.state)

  def draw(self,surf:Surface):
    s = self.states[self.state]
    r = s.get_rect()
    if self.rect_color is not None:
      draw.rect(surf,self.rect_color,self.rect)
    r.center = self.rect.center
    surf.blit(s,r)

class Switch(DrawBase):
  def __init__(self,pos:tuple[int,int],size:tuple[int,int],color_scheme:ColorScheme,callback:Callable[[bool],None]):
    self.rect = Rect(pos,size)
    self.callback = callback
    self.color_scheme = color_scheme
    self.state = False
    self.mhover = False
    self.clicking = False

  def setState(self,newState:bool):
    self.state = newState
    return self

  def update(self,input:Input):
    self.mhover = self.rect.collidepoint(input.mpos)
    if input.mb1d and self.mhover:
      self.clicking = True
      self.state = not self.state
      self.callback(self.state)
    elif input.mb1u and self.clicking:
      self.clicking = False

  def draw(self,surf:Surface):
    width = 0 if self.state else 2
    if self.clicking:
      color = self.color_scheme.getActive()
    elif self.mhover:
      color = self.color_scheme.getIdle()
    else:
      color = self.color_scheme.getInactive()
    draw.rect(surf,color,self.rect,width,4)

class Text(DrawBase):
  def __init__(self,pos:tuple[int,int],text:str,color:ColorType,font:font.Font):
    self.rect = Rect(pos,(0,0))
    self.font = font
    self.color = color
    self.on_rect_change_event:Event[[]] = Event()
    self.setText(text)
    self.showing = True

  def getText(self):
    return self.__text

  def setTextIfNeeded(self,newText:str):
    if self.__text != newText:
      self.setText(newText)

  def setText(self,newText:str) -> None:
    self.__text = newText
    self.surf = self.font.render(self.__text,True,self.color)
    self.rect.width = self.surf.get_width()
    self.on_rect_change_event.fire()

  def clear(self): self.setText('')

  def show(self): 
    self.showing = True
    return self
  
  def hide(self): 
    self.showing = False
    return self

  def draw(self,surf:Surface):
    if self.showing:
      surf.blit(self.surf,self.rect.topleft)

class AddText(DrawBase):
  __slots__ = 'color','f','obj','anchor_x','anchor_y','alignment_x','alignment_y','offset_x','offset_y','_final_offset_x','_final_offset_y','update','_s','onResize'
  def __init__(self,obj:HasRect,text:str,color:ColorType,f:font.Font,anchor_x:float = 0.5,anchor_y:float = 0.5,
                                                                     alignment_x:float = 0.5,alignment_y:float = 0.5,
                                                                     offset_x:int = 0,offset_y:int = 0):
    self.color = color
    self.f = f
    self.obj = obj
    self.anchor_x = anchor_x
    self.anchor_y = anchor_y
    self.alignment_x = alignment_x
    self.alignment_y = alignment_y
    self.offset_x = offset_x
    self.offset_y = offset_y
    self.rect = obj.rect
    self.setText(text)
    self.txt = ''

    if hasattr(obj,'update'):
      self.update = obj.update #type: ignore
    if hasattr(obj,'onResize'):
      self.onResize = obj.onResize#type: ignore

  def setText(self,text:str):
    self.txt = text
    self._s = self.f.render(text,True,self.color)
  
  def draw(self,surf:Surface):
    self.obj.draw(surf)
    surf.blit(self._s,
              (self.obj.rect.left+self.obj.rect.width*self.anchor_x-self._s.get_width()*self.alignment_x + self.offset_x,
               self.obj.rect.top+self.obj.rect.height*self.anchor_y-self._s.get_height()*self.alignment_y + self.offset_y)
              )

class AddImage(DrawBase):
  def __init__(self,obj:HasRect,img:Surface,anchor_x:float = 0.5,anchor_y:float = 0.5,offset_x:int = 0,offset_y:int = 0):
    self.obj = obj
    self.img = img
    self.anchor_x = anchor_x
    self.anchor_y = anchor_y
    self.offset_x = offset_x
    self.offset_y = offset_y
    if hasattr(obj,'update'):
      self.update = obj.update#type: ignore
    if hasattr(obj,'onResize'):
      self.onResize = obj.onResize#type: ignore

  @property
  def rect(self):
    return self.obj.rect
  
  def draw(self,surf:Surface):
    self.obj.draw(surf)
    surf.blit(self.img,
              (self.obj.rect.left+self.obj.rect.width*self.anchor_x-self.img.get_width()*self.anchor_x+self.offset_x,
               self.obj.rect.top+self.obj.rect.height*self.anchor_y-self.img.get_height()*self.anchor_y+self.offset_y)
              )

class Aligner:
  def __init__(self,obj:HasRect,anchor_x:float,anchor_y:float,alignment_x:float = 0.5,alignment_y:float = 0.5):
    self.obj = obj
    self.order_in_layer = obj.order_in_layer
    self.anchor = anchor_x,anchor_y
    self.alignment = alignment_x,alignment_y
    self.offset = self.obj.rect.topleft
    self.last_size:Optional[tuple[int,int]] = None
    if hasattr(obj,'update'):
      self.update = obj.update #type: ignore
    if hasattr(obj,'on_rect_change_event'):
      
      obj.on_rect_change_event.register( #type: ignore
        lambda : self.onResize(self.last_size) if self.last_size is not None else None
      )

  def onResize(self,size:tuple[int,int]):
    self.last_size = size
    if hasattr(self.obj,'onResize'): self.obj.onResize(size) #type: ignore
    r = self.obj.rect
    r.left = size[0] * self.anchor[0] - r.width * self.alignment[0] + self.offset[0]
    r.top = size[1] * self.anchor[1] - r.height * self.alignment[1] + self.offset[1]

  def draw(self,surf:Surface):
    self.obj.draw(surf)

class Resizer:
  @staticmethod
  def toPixels(s:str,l:int) -> int:
    if not s: return 0
    if '+' in s:
      toSum = s.split('+')
      return sum(Resizer.toPixels(s,l) for s in toSum)
    if '-' in s:
      s1,s2 = s.split('-')
      return (Resizer.toPixels(s1,l) - Resizer.toPixels(s2,l)) % l
    if s.isdigit():
      return int(s)%l
    elif s[-1] == '%':
      return int(float(s[:-1])* 0.01 * l)
    raise ValueError("Incorrect Format")
  
  def __init__(self,obj:HasRect,left:str,top:str,right:str,bottom:str):
    self.obj = obj
    self.left = left
    self.top = top
    self.right = right
    self.bottom = bottom
    self.order_in_layer = obj.order_in_layer
    if hasattr(obj,'update'):
      self.update = obj.update#type: ignore


  @property
  def rect(self):
    return self.obj.rect

  def onResize(self,size:tuple[int,int]):    
    obj = self.obj
    l = self.toPixels(self.left,size[0])
    t = self.toPixels(self.top,size[1])
    w = max(self.toPixels(self.right.replace('~',str(l)),size[0]) - l,0) 
    h = max(self.toPixels(self.bottom.replace('~',str(t)),size[1]) - t,0)
    if isinstance(self.obj,Space):
      newSpace = Space(Rect(l,t,w,h))
      self.update = newSpace.update #the update method that is cached must be redirected to point to the new object
      self.obj.resized(newSpace)
      self.obj = newSpace
      return 
    obj.rect.left = l
    obj.rect.top = t
    obj.rect.width = w
    obj.rect.height = h
    if hasattr(obj,'onResize'): obj.onResize(size) #type: ignore

  def draw(self,surf:Surface):
    self.obj.draw(surf)

class InputBox(DrawBase):
  def __init__(self,pos,size,color_layout:ColorLayout,caption = '',save_function:Callable|None =None,restrict_input = None):
    self.pos = pos
    self.font = font.SysFont('Courier New', 21)
    self.active = False
    self.caption = caption
    self.box_color = color_layout.background
    self.text_color = color_layout.foreground
    self.max_chars = 500
    self.text = ''
    self.textsurface = self.font.render(self.text, True, (0, 0, 0))
    self.rect = Rect(self.pos, size)
    self.max_chars_per_line = size[0]//12
    self.save_function = save_function if save_function else lambda x : x
    self.restrict_input = restrict_input
    self.timeactive = 0.0
    self.cursor_rect = Rect(0,0,2,18)
    self.surf = Surface(size,const.SRCALPHA)

  def resize(self,newSize:tuple[int,int]):
    self.rect.size = newSize
    self.max_chars_per_line = newSize[0]//12
    self.surf = Surface(newSize,const.SRCALPHA)
    self.redrawSurf()

  def setMaxChars(self,max:int):
    self.max_chars = max
    if len(self.text) > max: self.text = self.text[:max]
    return self

  def setText(self,new_text):
    self.text = new_text
    self.redrawSurf()

  def _checkKey(self,key:str,input:Input):
    if self.restrict_input and key not in self.restrict_input and key != u_const.BACK: return False
    if key == u_const.BACK:
      if len(self.text):    
        if input.lctrl:
          self.text = '' if ' ' not in self.text else ' '.join(self.text.split()[:-1])
        else:
          self.text = self.text[:-1]
      else:
        return False
    elif len(self.text) < self.max_chars:
      if key == '\r':
        key = '\n'
      self.text +=key
    if self.save_function:
      self.save_function(self.text)
    return True

  def update(self,input:Input):
    'mpos,mb1down,keys'
    mpos = input.mpos
    mb1down = input.mb1d
    if self.rect.collidepoint(mpos) and mb1down:
      self.active = True
      self.cursor_rect.topleft = (self.rect.left + (len(self.text)%self.max_chars_per_line)*12+2,self.rect.top+(len(self.text)//self.max_chars_per_line)*self.font.get_height()+2)
      self.timeactive = time.monotonic()
    elif mb1down:
      self.active = False
    if self.active:
      t = self.text
      input.KDQueue = list(filter(lambda x : not self._checkKey(x,input),input.KDQueue))
      if t != self.text: #if text has been updated
        self.timeactive = time.monotonic()-.5
        self.cursor_rect.topleft = (self.rect.left + (len(self.text)%self.max_chars_per_line)*12+2,self.rect.top+(len(self.text)//self.max_chars_per_line)*self.font.get_height()+2)
        self.redrawSurf()

  def redrawSurf(self):
    self.surf.fill((0,0,0,0))
    letters = [letter for letter in self.text]
    for char_num, letter in enumerate(letters):
      txt = self.font.render(letter, True, self.text_color)
      letterx = (char_num%self.max_chars_per_line)*12
      self.surf.blit(txt,(letterx,(char_num//self.max_chars_per_line)*self.font.get_height()))

  def draw(self,surf:Surface): 
    if self.box_color:
      draw.rect(surf,self.box_color,self.rect)
    if not self.text:
      self.textsurface = self.font.render(self.caption, True, self.text_color)
      surf.blit(self.textsurface,self.pos)
    else:
      surf.blit(self.surf,self.rect)
    if self.active and not int(time.monotonic()-self.timeactive) % 2:
      draw.rect(surf,(0,0,0),self.cursor_rect)

class InputBoxOneLine(DrawBase):
  def __init__(self,pos:tuple[int,int],size:tuple[int,int],color_layout:ColorLayout,callback:Callable[[str],None]|None,font:font.Font):
    self.rect = Rect(pos,size)
    self.color_layout = color_layout
    self.callback = callback
    self.max_chars = 999
    self.font = font
    self.surf = Surface(self.rect.size,const.SRCALPHA)
    self.surf.fill(self.color_layout.background)

    self.text = ''
    self.text_surf = Surface((0,0))
    self.cursor_position = 0
    self.cursor_height = self.font.get_height()
    self.cursor_visible_x = 0
    self.text_surf_left_shift = 0
    self.valid_keys = u_const.REGULAR
    self.text_y_alignment = 0.5
    self.active = False
    self.cursor_time = 0.0

  def onResize(self,newSize:tuple[int,int]):
    self.surf = Surface(self.rect.size,const.SRCALPHA)
    self.redrawSurf()

  def setRestrictInput(self,validKeys:set[str]|None):
    self.valid_keys = validKeys
  
  def setMaxChars(self,max:int):
    self.max_chars = max
    return self
  
  def setText(self,text:str):
    self.text = text
    if self.callback:
      self.callback(text)
    self.redrawSurf()
    return self
  
  def getXPosOfCursorPosition(self,c_position:int):
    return self.font.size(self.text[:c_position])[0] - self.text_surf_left_shift
  
  def resize(self,newSize:tuple[int,int]):
    self.rect.size = newSize
    self.onResize((0,0))

  def update(self,input:Input):
    mhover = self.rect.collidepoint(input.mpos)
    if input.mb1d:
      self.active = mhover
      if mhover:
        self.cursor_time = time.monotonic()
        self.cursor_position = binaryApproximate(self.getXPosOfCursorPosition,input.mousex-self.rect.left,0,len(self.text))
        self.cursor_visible_x = self.font.size(self.text[:self.cursor_position])[0]
    if self.active:
      if 'left_arrow' in input.KDQueue:
        self.cursor_position = max(0,self.cursor_position-1)
        self.redrawSurf()
        self.cursor_time = time.monotonic() - 0.5
      elif 'right_arrow' in input.KDQueue:
        self.cursor_position = min(len(self.text),self.cursor_position+1)
        self.redrawSurf()
        self.cursor_time = time.monotonic() - 0.5
      t = self.text
      input.KDQueue = list(filter(lambda c: not self.typeKey(c,input.lctrl,False),input.KDQueue))
      if t is not self.text:
        self.cursor_time = time.monotonic() - 0.5
        self.redrawSurf()
        if self.callback:
          self.callback(self.text)

  def backspace(self):
    if not self.text[:self.cursor_position]: return
    self.text = self.text[:self.cursor_position-1] + self.text[self.cursor_position:]
    self.cursor_position -= 1
    if self.cursor_position < 0: self.cursor_position = 0
  
  def currChar(self):
    if not self.cursor_position: return ''
    return self.text[self.cursor_position-1]

  def typeKey(self,key:str,lctrl:bool = False,use_callback:bool = True):
    if not key: return True
    if key == u_const.BACK:
      if lctrl:
        if self.currChar() == ' ': self.backspace()
        while self.currChar() not in {'',' '}:
          self.backspace()
      else:
        self.backspace()
      return True
    elif key == u_const.DELETE:
      if lctrl:
        pos_to_delete_to = self.text.find(' ',self.cursor_position)
        self.text = self.text[:self.cursor_position] + (self.text[pos_to_delete_to:] if pos_to_delete_to != -1 else '')
      else:
        self.text = self.text[:self.cursor_position] + self.text[self.cursor_position+1:]
          
    if self.valid_keys is not None and key not in self.valid_keys: return False
    if len(self.text) < self.max_chars:
      if key == u_const.ENTER:
        key = '\n'
      self.text = self.text[:self.cursor_position] + key + self.text[self.cursor_position:] 
      self.cursor_position += 1
    if self.callback and use_callback:
      self.callback(self.text)
    return True

  def redrawSurf(self):
    self.surf.fill(self.color_layout.background)
    self.text_surf = self.font.render(self.text,True,self.color_layout.foreground)
    if self.font.size(self.text)[0] < self.rect.width:
      self.text_surf_left_shift = 0
    self.cursor_visible_x = self.font.size(self.text[:self.cursor_position])[0]
    cursor_x_pos = self.cursor_visible_x - self.text_surf_left_shift
    if cursor_x_pos > self.rect.width-3:
      self.text_surf_left_shift += cursor_x_pos - self.rect.width + 3
    elif cursor_x_pos < 0:
      self.text_surf_left_shift += cursor_x_pos  
    self.surf.blit(self.text_surf,(-self.text_surf_left_shift,(self.rect.height - self.font.get_height())*self.text_y_alignment))

  def draw(self,surf:Surface):
    surf.blit(self.surf,self.rect)
    if not self.active: return
    t = int(time.monotonic() - self.cursor_time)
    if not t%2:
      draw.rect(surf,self.color_layout.foreground,(self.cursor_visible_x - self.text_surf_left_shift+self.rect.left,self.rect.top +(self.rect.height - self.font.get_height())*self.text_y_alignment,2,self.font.get_height()))

class Slider(DrawBase):
  def __init__(self,pos:tuple[int,int],size:tuple[int,int],color_layout:ColorLayout,save_function:Callable[[float],None]):
    self.pos = pos
    self.size = size
    self.rect = Rect(pos,size)
    self.save_function = save_function
    self.color = color_layout
    self.sliderx = 0
    self.value = 0.0
    # self.bar_rect = Rect(0,0,self.size[0],9)
    # self.bar_rect.midleft = (self.pos[0],self.pos[1]+self.size[1]//2)
    self.bar_width = 9
    self.active = False
    self.pactive = False
    self.mouse_active = False
 
  def onActivate(self): ...
  def onDeactivate(self): ...

  @property
  def passed_rect(self):
    return Rect(self.rect.left,self.rect.top+(self.rect.height-self.bar_width)//2,self.sliderx,self.bar_width)

  def setValue(self,x:float):
    if x < 0: x = 0
    elif x > 1: x = 1
    self.sliderx = self.rect.width*x
    self.value = x
    self.save_function(self.value)

  def update(self,input:Input):
    mpos,mb1down,mb1up = input.mpos,input.mb1d,input.mb1u
    if self.rect.collidepoint(mpos):
      self.mouse_active = True
      if mb1down:
        self.active = True
        self.onActivate()
    else:
      self.mouse_active = False
    if self.active and mb1up:
      self.active = False
      self.onDeactivate()

    if self.active:
      self.sliderx = min(max(mpos[0] - self.rect.left,0),self.rect.width)
      newVal = self.sliderx / self.rect.width
      if self.value != newVal:
        self.value = newVal
        self.save_function(self.value)

    self.pactive = self.active

  def draw(self,surf:Surface):
      draw.rect(surf,self.color.background,(self.rect.left,self.rect.top+(self.rect.height-self.bar_width)//2,self.rect.width,self.bar_width),0,2)
      # draw.rect(surf,self.passed_color,self.passed_rect,0,2)
      draw.circle(surf,self.color.foreground,(self.sliderx+self.rect.left,self.rect.midleft[1]),7)

class SquareSlider(Slider):
  def __init__(self, pos: tuple[int, int], size: tuple[int, int], color_layout: ColorLayout,range:Iterable,save_function: Callable[[int], None],initial_value:int|None = None):
    self.values = list(range)
    super().__init__(pos,size,color_layout,self.save_wrapper)
    self.bar_width = size[1]
    self.save = save_function
    self.last_value = None
    self.slider_rect = Rect(0,pos[1],5,size[1])
    if initial_value is not None:
      assert initial_value in self.values, 'Initial Value must in set of valid values'
      self.setValue(initial_value)

  def save_wrapper(self,value:float) -> None:
    value = self.sliderx / (self.rect.width + 1)
    index = int(value * len(self.values))
    v = self.values[index]
    if v != self.last_value:
      self.last_value = v
      self.save(v)
    
  def draw(self,surf:Surface):
    draw.rect(surf,self.color.background,self.rect,0,2)
    self.slider_rect.left  = self.rect.left + (self.rect.width - self.slider_rect.width) * self.value
    draw.rect(surf,self.color.foreground,self.slider_rect,0,2)

  def setValue(self,value:int):
    try:
      index = self.values.index(value)
      super().setValue(index / (len(self.values)-1))
    except ValueError:
      raise ValueError("Value not found in valid values")

class KeyBoundFunction:
  __slots__ = 'func','keys','offSetPos'
  def __init__(self,func:EventHook|Callable[[],Any],*keys:str):
    self.func = func
    self.keys = set(keys)

  def update(self,input:Input) -> None:
    #find all keys that we accept, if list is empty return
    if in_both := self.keys.intersection(input.KDQueue):
      for key in in_both:
        input.KDQueue.remove(key)
      self.func()

class Button(DrawBase):
  rect:Rect
  def __init__(self,pos:tuple[int,int],size:tuple[int,int],color_scheme:ColorScheme,onDownFunction:EventHook|EventHookAny|None=None,onUpFunction:EventHook|EventHookAny|None=None):
    self.rect = Rect(pos,size)
    self.color_scheme = color_scheme
    self.onDown = onDownFunction
    self.onUp = onUpFunction
    self.state = 0 #0 -> up, 1 -> hover, 2 -> down

  def setToUp(self):
    if self.state == 2 and self.onUp is not None:
      self.onUp()
    self.state = 0

  def update(self,input:Input):
    if self.rect.collidepoint(input.mpos):
      if self.state == 0:
        self.state = 1
      if input.mb1d == 1:
        self.state = 2
        if input.mb1d and self.onDown is not None:
          self.onDown()
    else:
      if self.state == 1:
        self.state = 0
  
    if self.state == 2:
      if input.mb1u:
        self.state = 1
        if self.onUp is not None:
          self.onUp() 

  def draw(self,surf:Surface):
    cs = self.color_scheme
    color = [cs.getInactive,cs.getIdle,cs.getActive][self.state]() #TODO find out if its worth it to cache the results instead of calling them everytime
    draw.rect(surf,color,self.rect)

class SelectionBase(Button):
  def __init__(self,pos:tuple[int,int],size:tuple[int,int],color_scheme:ColorScheme,onDown:EventHook|None = None,onUp:EventHook|None = None) -> None:
    self.pos = pos
    super().__init__(pos,size,color_scheme,onDown,onUp)
    self.setYOffset(0)  

  def onYOffsetChangeHook(self,offsetY:int): ...
  def getYOffSet(self) -> int: return self.yoffset

  def setYOffset(self,y:int): 
    self.yoffset = y
    self.rect.top = self.pos[1] - y
    self.onYOffsetChangeHook(y)

class Selection(DrawBase):
  def __init__(self,pos:tuple[int,int],selectionSize:tuple[int,int],max_y:int,color_scheme:ColorScheme,dataGetter:Callable[[],Iterable[T]],buttonFactory:Callable[[tuple[int,int],tuple[int,int],ColorScheme,T],SelectionProtocol]=SelectionBase,spacing:float = 1):
    self.rect = Rect(pos,(selectionSize[0],max_y))
    self.selectionSize = selectionSize
    self.max_y = max_y
    self.buttonFactory = buttonFactory
    self.dataGetter = dataGetter
    self.selection:list[SelectionProtocol] = []
    self.y_scroll_real:int = 0
    self.y_scroll_target:int = 0 
    self.aligned_y = True
    self.mhover = False
    self.color_scheme = color_scheme
    self.spacing = spacing
    self.size_change_event:Event[[]] = Event()
    self.surf = Surface(self.rect.size,const.SRCALPHA)
    self.pwheel = 0
    self.recalculateSelection()
    
  def recalculateSelection(self):
    self.selection = [self.buttonFactory((0,(self.selectionSize[1]*i*self.spacing).__trunc__()),self.selectionSize,self.color_scheme,d) for i,d in enumerate(self.dataGetter())]
    self.size_change_event.fire()
    
    if self.fullHeight < self.max_y:
      self.setYScroll(0)
    elif self.fullHeight + self.y_scroll_real < self.max_y:
      self.setYScroll(self.fullHeight-self.max_y)
    else:
      for s in self.selection:
        s.setYOffset(self.y_scroll_real)
  def resize(self,newPos:tuple[int,int],newSelectionSize:tuple[int,int],new_max_y:int):
    self.rect.topleft = newPos
    self.rect.width = newSelectionSize[0]
    self.rect.height = new_max_y
    self.selectionSize = newSelectionSize
    self.max_y = new_max_y
    self.recalculateSelection()
    self.setYScroll(self.y_scroll_real)

  def onResize(self,size:tuple[int,int]):
    self.max_y = self.rect.height
    self.selectionSize = (self.rect.width,self.selectionSize[1])
    self.recalculateSelection()
    if self.fullHeight < self.max_y:
      self.y_scroll_real = 0
    elif self.y_scroll_real > self.fullHeight - self.max_y:
     self.y_scroll_real = self.fullHeight - self.max_y  
    self.setYScroll(self.y_scroll_real)
    # print('new Size!',self.rect.size)
    if self.rect.size != self.surf.get_size():
      self.surf = Surface(self.rect.size,const.SRCALPHA)

  @property
  def fullHeight(self):
    return (len(self.selection) * self.selectionSize[1] * self.spacing).__trunc__()

  def getScrollPercent(self):
    fullHeight = self.fullHeight
    usableHieght = self.max_y
    if usableHieght > fullHeight:
      return 1.0
    return self.y_scroll_real / (fullHeight - usableHieght)

  def setScrollPercent(self,percent:float):
    fullHeight = self.fullHeight
    usableHieght = self.max_y
    if usableHieght <= fullHeight:
      self.setYScroll((percent *(fullHeight - usableHieght)).__round__())

  def setYScroll(self,y:int):
    self.aligned_y = False
    self.y_scroll_real = self.y_scroll_target = y
    for s in self.selection:
      s.setYOffset(self.y_scroll_real)

  def update(self,input:Input):
    mpos,wheel = input.mpos,input.wheel
    if self.rect.collidepoint(mpos):  
      self.mhover = True      
      if wheel and self.fullHeight > self.max_y:
        w = (wheel + self.pwheel.__trunc__()) * WHEEL_SENSITIVITY
        self.y_scroll_target += w
        if self.y_scroll_target > self.fullHeight - self.max_y:
          self.y_scroll_target = self.fullHeight - self.max_y
        elif self.y_scroll_target < 0: self.y_scroll_target = 0
        self.aligned_y = False
      input.mousex -= self.rect.left
      input.mousey -= self.rect.top
      for i,button in enumerate(self.selection):
        top = (i*self.selectionSize[1]*self.spacing).__trunc__() - self.y_scroll_real
        bottom = top + self.selectionSize[1]
        if bottom < 0 or top > self.max_y: continue
        button.update(input)
      input.mousex += self.rect.left
      input.mousey += self.rect.top
    else:
      if self.mhover:
        for s in self.selection:
          s.setToUp()
        self.mhover = False
      if input.mb1d or input.mb1u or input.mb3u or input.mb3d:
        mx,my = input.mpos
        input.mousex = -999
        input.mousey = -999
        for button in self.selection:
          button.update(input)
        input.mousey = my
        input.mousex = mx
      
    if not self.aligned_y:
      self.y_scroll_real = (self.y_scroll_real + (self.y_scroll_target - self.y_scroll_real) * min(1/6,1)).__round__()        
      if (self.y_scroll_real - self.y_scroll_target).__abs__() < 2:
        self.y_scroll_real = self.y_scroll_target
        self.aligned_y = True
      for s in self.selection:
        s.setYOffset(self.y_scroll_real)
    self.pwheel = self.pwheel + wheel * 0.5 if wheel else 0

  def draw(self,surf:Surface):
    surf2 = surf.subsurface(self.rect)
    for i,s in enumerate(self.selection):
      top = (i*self.selectionSize[1]*self.spacing).__trunc__() - self.y_scroll_real
      bottom = top + self.selectionSize[1]
      if bottom < 0 or top > self.max_y: continue
      s.draw(surf2)
    # surf.blit(self.surf,self.rect)

class Scrollbar(DrawBase):
  def __init__(self,pos:tuple[int,int],size:tuple[int,int],scrollbar_size:int,color_layout:ColorLayout) -> None:
    self.pos = pos
    self.scroll_size = scrollbar_size
    self.usable_size = size[1]-scrollbar_size
    self.rect = Rect(pos,size)
    self.color_layout = color_layout

    self.mouse_down_offset = 0
    self.x = 0
    self._drag_rect = Rect(self.pos[0],self.pos[1],size[0],scrollbar_size)

    self.state:Literal["Dragging",'Hover Scroll','Hover','Off'] = 'Off'
    self.linked_dropdown:Optional[SelectionLike] = None
    self.hiding = False

  def onResize(self,size:tuple[int,int]):
    if self.linked_dropdown:
      self.adjustSize()

  def linkToDropdown(self,dropdown:SelectionLike, auto_adjust = True):
    self.linked_dropdown = dropdown
    if auto_adjust:
      dropdown.size_change_event.register(self.adjustSize)
      self.adjustSize()
    return self
  
  def adjustSize(self):
    assert self.linked_dropdown
    try:
     x = self.linked_dropdown.max_y/self.linked_dropdown.fullHeight 
    except ZeroDivisionError:
      x = float('inf')

    if x >=1:
      self.hiding = True
    else:
      self.hiding = False

      self.rect.left = self.linked_dropdown.rect.right
      self.rect.height = self.linked_dropdown.max_y
      self.scroll_size =(x * self.rect.height).__trunc__()
      self.usable_size = self.rect.height-self.scroll_size
      self._drag_rect.left = self.rect.left
      self._drag_rect.height = self.scroll_size 

  def update(self,input:Input):
    if self.hiding: return
    mpos,mb1d,mb1u = input.mpos,input.mb1d,input.mb1u
    if self.rect.collidepoint(mpos) and self.state != 'Dragging':
      self.state = 'Hover Scroll' if self._drag_rect.collidepoint(mpos) else 'Hover'
      if mb1d and self.state =='Hover Scroll':
        self.mouse_down_offset = mpos[1] - self._drag_rect.top
        self.state = 'Dragging'
    if mb1u and self.state == 'Dragging':
      self.state = 'Off'

    if self.state == 'Dragging':
      self._drag_rect.top = mpos[1] - self.mouse_down_offset
      if self._drag_rect.top < self.rect.top: self._drag_rect.top = self.rect.top
      if self._drag_rect.bottom > self.rect.bottom: self._drag_rect.bottom = self.rect.bottom
      self.x = self._drag_rect.top - self.rect.top 
      if self.linked_dropdown:
        self.linked_dropdown.setScrollPercent(self.getValue())
    else:
      if self.linked_dropdown:
        self.setValue(self.linked_dropdown.getScrollPercent())

  def getValue(self):
    return min(self.x / self.usable_size,1)

  def setValue(self,value:float):
    self.x = value * self.usable_size
    self._drag_rect.top = self.rect.top + self.x
        
  def draw(self,surf:Surface):
    if self.hiding: return
    draw.rect(surf,self.color_layout.background,self.rect)
    draw.rect(surf,self.color_layout.foreground,self._drag_rect)

class ScrollbarConsuming(Scrollbar):
  def update(self,input:Input):
    super().update(input)
    if self.state == 'Hover Scroll' or self.state == 'Dragging':
      input.mousex = -999
      input.mousey = -999

class ClearInput:
  def update(self,input:Input):
    input.clearALL()

class Layer(DrawBase):
  def __init__(self,size:tuple[int,int]):
    self.rect = Rect(0,0,size[0],size[1])
    self.next_layer: Layer|None = None
    self.space = Space(self.rect.copy())

  def onResize(self,size:tuple[int,int]):
    new = Space(self.rect.copy())
    self.space.resized(new)
    self.space = new
    if self.next_layer:
      self.next_layer.resize(size)

  def resize(self,newSize:tuple[int,int]):
    self.rect.size = newSize
    new = Space(self.rect.copy())
    self.space.resized(new)
    self.space = new
    if self.next_layer:
      self.next_layer.resize(newSize)

  def resetEverything(self,newSize:tuple[int,int]|None=None):
    if newSize is not None:
      self.rect.size = newSize
    if self.next_layer:
      self.removeLayer(self.next_layer,True)
    self.space = Space(self.rect.copy())

  def update(self,input:Input):
    if self.next_layer:
      self.next_layer.update(input)
    self.space.update(input)
  
  def draw(self,surf:Surface):
    self.space.draw(surf)
    if self.next_layer:
      self.next_layer.draw(surf)

  def addLayer(self,layer:Optional["Layer"] = None) -> "Layer":
    if self.next_layer:
      return self.next_layer.addLayer(layer)
    if layer is not None:
      layer.resize(self.rect.size)
      self.next_layer = layer
    else:
      self.next_layer = Layer(self.rect.size) 
    return self.next_layer
  
  def removeLayer(self,layer:"Layer",and_all_after:bool = False) -> bool:
    if self.next_layer is not layer:
      if self.next_layer:
        return self.next_layer.removeLayer(layer,and_all_after)
      else:
        return False
    else:
      if and_all_after:
        self.next_layer = None
      else:
        self.next_layer = layer.next_layer
      return True

class Space:
  order_in_layer = 0
  def __init__(self,rect:Rect):
    self.rect = rect
    self.to_update:list[SupportsUpdate] = []
    self.to_draw:list[SupportsDraw] = []
    self.sub_spaces:list[Space] = []
    self.splits:list[tuple[int,int]] = []
    
    self.is_container = False
    self.container_copies:dict[str,tuple[list[SupportsUpdate],list[SupportsDraw]]] = {}
    self.active_container:str = ''
    
  def makeContainer(self,ui_elements:dict[str,list[SupportsDraw|SupportsUpdate]],active:str,shared_elements:list[SupportsDraw|SupportsUpdate] = []):
    if self.to_draw or self.to_update: raise RuntimeError("Cannot Make Space that already contains elements into Container")
    assert active in ui_elements, '<active> must be a key in the dict <container_copies>'
    self.is_container = True
    for key,l in ui_elements.items():
      self.to_update,self.to_draw = [],[]
      self.addObjects(*l)
      self.addObjects(*shared_elements)
      self.container_copies[key] = (self.to_update,self.to_draw)
    self.setActive(active)
    return self

  def copyEmptyShallow(self):
    '''Returns a new Space with the same size with no sub_spaces or UIElements and not as a container'''
    return Space(self.rect.copy())
  
  def addObject(self,obj:T) -> T:
    '''Will add a UI element to the Space, if this Space is a Container, it adds the element to the currently loaded element list
    Returns UI element'''
    if hasattr(obj,'update'):
      self.to_update.append(obj)#type: ignore
    if hasattr(obj,'draw'):
      self.to_draw.append(obj) #type: ignore
      self.to_draw.sort(key=lambda d:d.order_in_layer)
      if hasattr(obj,'onResize'):
        obj.onResize(self.rect.size) #type: ignore
    return obj
  def removeObject(self,obj:SupportsUpdate|SupportsDraw):
    if self.is_container:
      for u,d in self.container_copies.values():
        if obj in u:
          u.remove(obj)#type: ignore
        if obj in d:
          d.remove(obj)
    else:
      if hasattr(obj,'update'):
        self.to_update.remove(obj)#type: ignore
      if hasattr(obj,'draw'):
        self.to_draw.remove(obj) #type: ignore

  def clear(self):
    if self.is_container:
      for u,d in self.container_copies.values():
        u.clear()
        d.clear()
    else:
      self.to_update.clear()
      self.to_draw.clear()
    
    

  def addObjects(self,*objs:SupportsUpdate|SupportsDraw):
    '''Add UIElements in bulk, for more info read addObject docstring'''
    for obj in objs:
      self.addObject(obj)

  def setActive(self,key:str):
    if not self.is_container: raise RuntimeError("Active Key only applies for Container's")
    self.to_update, self.to_draw = self.container_copies[key]
    self.active_container = key

  def getActive(self) -> str:
    if not self.is_container: raise RuntimeError("Active Key only applies for Container's")
    return self.active_container

  def resized(self,space:"Space"):
    '''
    This function is a little confusing, but its main purpose is to take in a blank <Space> object and partition it
    exactly how itself is, however the blank <Space> object may be of different size than this object
    '''
    for (direction,amount),sub in zip(self.splits,self.sub_spaces):
      f = [space.cutTopSpace,space.cutBottomSpace,space.cutLeftSpace,space.cutRightSpace][direction]
      sub.resized(f(amount))
    if self.is_container:
      space.container_copies = self.container_copies
      space.is_container = True
      space.to_update = self.to_update
      space.to_draw = self.to_draw
      space.active_container = self.active_container
      for _u,draw in self.container_copies.values():
        for d in draw: #type: ignore
          if hasattr(d,'onResize'):
            d:SupportsResize
            d.onResize(space.rect.size)
    else:
      space.to_update = self.to_update
      space.to_draw = self.to_draw
      for d in self.to_draw: #type: ignore
        if hasattr(d,'onResize'):
          d:SupportsResize
          d.onResize(space.rect.size) 

  def update(self,input:Input):
    l,t = self.rect.topleft #store topleft just in case it changes from updates
    input.mousex -= l
    input.mousey -= t
    for u in self.to_update:
      u.update(input)
    input.mousex += l
    input.mousey += t

    for s in self.sub_spaces:
      s.update(input)
  
  def draw(self,surf:Surface):
    s= surf.subsurface(self.rect)
    for d in self.to_draw:
      d.draw(s)

    for s in self.sub_spaces:
      s.draw(surf)


  def cutTopSpace(self,amount:int) -> "Space":
    new = Space(Rect(self.rect.left,self.rect.top,self.rect.width,amount))
    self.rect.height -= amount
    self.rect.top += amount
    self.splits.append((0,amount)) 
    self.sub_spaces.append(new)
    return new
  
  def cutBottomSpace(self,amount:int) -> "Space":
    new = Space(Rect(self.rect.left,self.rect.bottom-amount,self.rect.width,amount))
    self.rect.height -= amount
    self.splits.append((1,amount)) 
    self.sub_spaces.append(new)
    return new
  
  def cutLeftSpace(self,amount:int) -> "Space":
    new = Space(Rect(self.rect.left,self.rect.top,amount,self.rect.height))
    self.rect.left += amount
    self.rect.width -= amount
    self.splits.append((2,amount)) 
    self.sub_spaces.append(new)
    return new
  
  def cutRightSpace(self,amount:int) -> "Space":
    self.rect.width -= amount
    new = Space(Rect(self.rect.right,self.rect.top,amount,self.rect.height))
    self.splits.append((3,amount)) 
    self.sub_spaces.append(new)
    return new

base_layer = Layer((0,0))

def minimize(): '''Minimize screen'''; return display.iconify()

def init(size:tuple,name:str = 'pygame window',flags = 0,**kwargs) -> Surface:
  #nerf miner
  global saved_flags
  curr = pygame.display.get_surface()
  if curr is None:
    saved_flags = flags
    if size[0] == 0: size = (MONITOR_WIDTH,size[1])
    if size[1] == 0: size = (size[0],MONITOR_HEIGHT)
    screen = display.set_mode(size,flags,**kwargs)
    display.set_caption(name)
  scrap.init()
  return screen

def setMinScreenSize(x:int,y:int) -> None:
  global minScreenX,minScreenY
  minScreenX = x
  minScreenY = y

def findAllFiles(ending:str,addedPath:str = ''):
  '''Find all files with a specific extension like .png or .txt'''
  for _root, _dirs, files in walk('./'+addedPath): 
    for file in files:
      if file.endswith(ending):
        yield str(file)

def setWindowIcon(surf:Surface) -> None:
  display.set_icon(surf)

def loadImg(path:str,useAlpha:bool = False) -> Surface:
  '''Returns a pygame Surface of image provided with FileName\n
  Use Alpha for Images that should have a transparent background''' 
  if useAlpha:
    return image.load(path).convert_alpha()
  else:
    return image.load(path).convert()


def aaarc(source:Surface,color:tuple[int,int,int]|str,center:tuple[float,float],radius:float,start_angle:float,end_angle:float,resolution:int = 0):
  #if end_angle < start_angle: end_angle += 2*3.141592653589
  from math import cos,sin
  #if start_angle > end_angle: return
  if start_angle==end_angle: return
  points = [center]
  dif = end_angle-start_angle
  resolution = max(int(dif*10),1) if resolution <= 0 else resolution
  for i in range(resolution+1):
    a = start_angle + i*dif/resolution
    points.append((center[0] + cos(a)*radius,center[1]-sin(a)*radius))
  gfxdraw.aapolygon(source,points,color)
  gfxdraw.filled_polygon(source,points,color)


@Input_.onEvent(const.VIDEORESIZE)
def onVIDEORESIZE(i:Input,e:Input_.event.Event):
  w,h = display.get_window_size()
  if (h < minScreenY or w < minScreenX):
    display.set_mode((max(w,minScreenX),max(h,minScreenY)),saved_flags)


