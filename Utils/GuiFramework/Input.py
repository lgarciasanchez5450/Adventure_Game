from typing import Callable
from pygame import event
from pygame import constants as const
from pygame import mouse
from pygame import display
from pygame.scrap import get
from .unicode_constants import PASTE


__all__ = [
    'Input',
    'getInput',
    'onEvent'
]

class Input:
    '''
    A way to dump all the input gathered by getAllInput() so that it can be directly put into
    update methods so that they can pick what they need to update things.
    '''
    w:int = 0
    a:int = 0
    s:int = 0
    d:int = 0
    space:int = 0
    mousex:int
    mousey:int
    mb1:bool
    mb2:bool
    mb3:bool
    lctrl:bool = False
    lalt:bool = False
    lshift:bool = False
    rctrl:bool = False
    ralt:bool = False
    rshift:bool = False

    def __init__(self):
        self.Events  = set() 
        self.KDQueue = []
        self.KUQueue = []
        self.dt = 0
        self.wheel:int = 0
        self.quitEvent = False
        self.mb1d:bool = False
        self.mb2d:bool = False
        self.mb3d:bool = False
        self.mb1u:bool = False
        self.mb2u:bool = False
        self.mb3u:bool = False

    @property
    def mpos(self): return self.mousex,self.mousey

    def clearALL(self):
        self.clearMouse()
        self.clearKeys()
        self.__init__()
        

    def clearMouse(self):
        self.mb1d = self.mb2d = self.mb3d = self.mb1u = self.mb2u = self.mb3u = self.mb1 = self.mb2 = self.mb3 = False
        self.mousex = self.mousey = -999

    def clearKeys(self):
        self.KUQueue.clear()
        self.KDQueue.clear()
        self.lctrl = self.lalt = self.lshift = self.rctrl = self.ralt = self.rshift = False
        self.w = self.a = self.s = self.d = 0

_event_dispatch:dict[int,list[Callable[[Input,event.Event],None]]] = {}

def onEvent(e):
    def decorator(func:Callable[[Input,event.Event],None]):
        if e not in _event_dispatch:
            _event_dispatch[e] = []
        _event_dispatch[e].append(func)
    return decorator

key_aliases = {const.K_LEFT:'left_arrow',const.K_RIGHT:'right_arrow',const.K_UP:'up_arrow',const.K_DOWN:'down_arrow'}



@onEvent(const.KEYDOWN)    
def onKEYDOWN(input:Input,event:event.Event):
    global key_aliases
    input.KDQueue.append(key_aliases.get(event.key,event.unicode))
    if event.unicode == PASTE:
        scrap = (get(const.SCRAP_TEXT) or b'').decode()
        for letter in scrap:
            input.KDQueue.append(letter)
    elif event.key == const.K_LCTRL:
        Input.lctrl = True
    elif event.key == const.K_LALT:
        Input.lalt = True
    elif event.key == const.K_RCTRL:
        Input.rctrl = True
    elif event.key == const.K_RALT:
        Input.ralt = True
    elif event.key == const.K_w:
        Input.w = 1
    elif event.key == const.K_a:
        Input.a = 1
    elif event.key == const.K_s:
        Input.s = 1
    elif event.key == const.K_d:
        Input.d = 1
    elif event.key == const.K_SPACE:
        Input.space = 1
    elif event.key == const.K_LSHIFT:
        Input.lshift = True
    elif event.key == const.K_RSHIFT:
        Input.rshift = True

@onEvent(const.KEYUP)
def onKEYUP(input:Input,event:event.Event):
    input.KUQueue.append(event.unicode)
    if event.key == const.K_LCTRL:
        Input.lctrl = False
    elif event.key == const.K_LALT:
        Input.lalt = False
    elif event.key == const.K_RCTRL:
        Input.rctrl = False
    elif event.key == const.K_RALT:
        Input.ralt = False
    elif event.key == const.K_w:
        Input.w = 0
    elif event.key == const.K_a:
        Input.a = 0
    elif event.key == const.K_s:
        Input.s = 0
    elif event.key == const.K_d:
        Input.d = 0
    elif event.key == const.K_SPACE:
        Input.space = 0
    elif event.key == const.K_LSHIFT:
        Input.lshift = False
    elif event.key == const.K_RSHIFT:
        Input.rshift = False
onEvent(const.QUIT)(lambda i,e: setattr(i,'quitEvent',True))

@onEvent(const.MOUSEBUTTONDOWN)
def onMOUSEBUTTONDOWN(i:Input,e:event.Event):
    if e.button == 1:
        i.mb1d = True
    elif e.button == 2:
        i.mb2d = True
    elif e.button == 3:
        i.mb3d = True
    elif e.button == 4:
        i.wheel -= 1
    elif e.button == 5:
        i.wheel += 1

@onEvent(const.MOUSEBUTTONUP)
def onMOUSEBUTTONUP(i:Input,e:event.Event):
    if e.button ==1:
        i.mb1u = True
    elif e.button == 2:
        i.mb2u = True
    elif e.button == 3:
        i.mb3u = True

def getInput() -> Input:
    input = Input()
    Input.mousex,Input.mousey = mouse.get_pos()
    input.mb1,input.mb2,input.mb3 = mouse.get_pressed()
    for e in event.get():
        input.Events.add(e.type)
        if l:=_event_dispatch.get(e.type):
            for f in l: f(input,e)
    return input
