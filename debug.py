import pygame,ctypes,sys
from time import perf_counter as time
from collections import deque
from game_math import *
import gc
gc.disable()
pygame.init()
def init(display:pygame.Surface):
    global surf
    surf = display

font = pygame.font.SysFont('Arial',30,1)
font15 = pygame.font.SysFont('Arial',15)
surf:pygame.Surface|None = None
def debug(info,pos = (10,10)):
    global surf
    if surf is None:return
    surf.blit(font.render(str(info),True,(255,255,255)),pos)

times:dict[str,list] = {}
def profile(func):
    times[str(func.__name__)] = []
    def inner(*args,**kwargs):
        global times 
        start = time()
        value = func(*args,**kwargs)
        end = time()
        times[str(func.__name__)].append(end-start)
        print(f"{func.__name__} took {end - start} seconds")
        return value
    return inner

def getMemoryUsed():
    '''Returns bytes used by python'''
    import psutil
    process = psutil.Process()
    return (process.memory_info().rss)  # in bytes 

def getrefcount(memory_addres):
    raise DeprecationWarning('Use sys.getreferencecountinstead!')
    assert isinstance(memory_addres,int),"must pass in memory address by using id(variable) and not the variable itself"
    return ctypes.c_long.from_address(memory_addres).value

class MemoryTracker:
    COLOR = (0,255,0)
    def __init__(self,tracking_size:int = 100,screen_pos:tuple = (400,20),every:int = 10):
        self.t_size = tracking_size
        self.track = deque([0]*tracking_size,tracking_size)
        self.min = float('inf')
        self.max = float('-inf')
        self.screen_pos = screen_pos

        self.surface = pygame.Surface((tracking_size,100))
        self.every = every
        self.frames_left= every



    def update_surf(self):
        self.surface.lock()
        self.surface.fill((50,50,50))
        dif = (self.max - self.min)
        if dif == 0:
            dif = 1
        for x,mag in enumerate(self.track):
            self.surface.set_at((x,90-round((mag-self.min)/dif*80)),self.COLOR)
        self.surface.unlock()
        self.surface.blit(font15.render(str(round(self.max,4)),True,'white'),(0,0))
        self.surface.blit(font15.render(str(round(self.min,4)),True,'white'),(0,100-20))



    def update(self):
        self.frames_left -= 1
        if self.frames_left != 0 : return 
        self.frames_left = self.every
        mem = getMemoryUsed()//(2**20)
        self.track.append(mem)
        if mem < self.min:
            self.min = mem
        elif mem > self.max:
            self.max = mem
        self.update_surf()


    def draw(self):
        if surf is None: return
        surf.blit(self.surface,self.screen_pos)
class VecTracker:
    X_COLOR = (60,60,255)
    Y_COLOR = (255,0,0)
    MAGNITUDE_COLOR = (0,255,0)
    #'''TRACKING MODES'''
    X = 0b1
    Y = 0b10
    MAGNITUDE = 0b100
    def __init__(self,vec:Vector2,tracking_size:int = 100,mode:int = 0,screen_pos:tuple = (400,20),every:int = 10):
        self.mode = 0
        self.setMode(mode)
        self.vec = vec
        self.t_size = tracking_size
        self.trackx = deque([0.0]*tracking_size,tracking_size)
        self.tracky = deque([0.0]*tracking_size,tracking_size)
        self.trackmag = deque([0.0]*tracking_size,tracking_size)
        self.min = float('inf')
        self.max = float('-inf')
        self.screen_pos = screen_pos

        self.surface = pygame.Surface((tracking_size,100))
        self.every = every
        self.frames_left= every


    def setMode(self,mode:int):
        modes_that_changed = mode ^ self.mode
        self.mode = mode
        
        if modes_that_changed & 0b001 & ~mode:# we are tracking x
            for _ in range(self.t_size):
                self.trackx.append(0)
        if modes_that_changed & 0b010 & ~mode:
            for _ in range(self.t_size):
                self.tracky.append(0)  
        if modes_that_changed & 0b100 & ~mode:
            for _ in range(self.t_size):
                self.tracky.append(0)

    def update_surf(self):
        self.surface.lock()
        self.surface.fill((50,50,50))
        dif = (self.max - self.min)
        if dif == 0:
            dif = 1
        if self.mode & 0b001:
            for x,x2 in enumerate(self.trackx):
                self.surface.set_at((x,90-round((x2-self.min)/dif*80)),self.X_COLOR)
        if self.mode & 0b010:
            for x,y in enumerate(self.tracky):
                self.surface.set_at((x,90-round((y-self.min)/dif*80)),self.Y_COLOR)
        if self.mode & 0b100:
            for x,mag in enumerate(self.trackmag):
                self.surface.set_at((x,90-round((mag-self.min)/dif*80)),self.MAGNITUDE_COLOR)
        self.surface.unlock()
        self.surface.blit(font15.render(str(round(self.max,4)),True,'white'),(0,0))
        self.surface.blit(font15.render(str(round(self.min,4)),True,'white'),(0,100-20))


    def update(self):
        self.frames_left -= 1
        if self.frames_left != 0 : return 
        self.frames_left = self.every
        if self.mode & 0b001:
            x = self.vec.x
            self.trackx.append(x)
            if x < self.min:
                self.min = x
            elif x > self.max:
                self.max = x
        if self.mode & 0b010:
            y = self.vec.y
            self.tracky.append(y)
            if y < self.min:
                self.min = y
            elif y > self.max:
                self.max = y       
        if self.mode & 0b100:
            mag = self.vec.magnitude()
            self.trackmag.append(mag)
            if mag < self.min:
                self.min = mag
            elif mag > self.max:
                self.max = mag
        self.update_surf()


    def draw(self):
        if surf is None: return
        surf.blit(self.surface,self.screen_pos)