from typing import Callable
import pygame,ctypes,sys
from time import perf_counter as time
from collections import deque
from Utils.Math.Vector import *
import numpy as np
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
def profile_as(name:str):
    times[str(name)] = []
    def wrapper(func):
        def inner(*args,**kwargs):
            global times 
            start = time()
            value = func(*args,**kwargs)
            end = time()
            times[str(name)].append(end-start)
            if (end - start) > 0.00001:
                print(f"{name} took {end - start} seconds")
            return value
        return inner
    return wrapper
def profile(func):
    times[str(func.__name__)] = []
    def inner(*args,**kwargs):
        global times 
        start = time()
        value = func(*args,**kwargs)
        end = time()
        times[str(func.__name__)].append(end-start)
        if (end - start) > 0.0000001:
            print(f"{func.__name__} took {end - start} seconds")
        return value
    return inner

def getMemoryUsed():
    '''Returns bytes used by python'''
    import psutil #type:ignore
    process = psutil.Process()
    return (process.memory_info().rss)  # in bytes 

def getrefcount(memory_addres):
    raise DeprecationWarning('Use sys.getreferencecount instead!')
    assert isinstance(memory_addres,int),"must pass in memory address by using id(variable) and not the variable itself"
    return ctypes.c_long.from_address(memory_addres).value

def model_function(func:Callable,xs:np.ndarray):
    from matplotlib import pyplot
    pyplot.plot(xs,func(xs))
    pyplot.show()
from time import perf_counter
class Tracer:
    singleton = None
    @classmethod
    def new(cls):
        return super(cls).__new__(cls)
            
    def __new__(cls):
        if Tracer.singleton is None:
            Tracer.singleton = object.__new__(cls)
        return Tracer.singleton
        
    def __init__(self):
        self.calls:deque[tuple[int,float,str]] = deque()
        self.running = False

    def trace(self,func:Callable):
        def wrapper(*args,**kwargs):
            if self.running:
                self.calls.append((0,perf_counter(),func.__name__))
                try:
                    val = func(*args,**kwargs)
                finally:
                    self.calls.append((1,perf_counter(),func.__name__))
                return val
            return func(*args,**kwargs)
        return wrapper
    
    def show(self):
        if not self.calls:
            return
        pygame.quit()
        pygame.init()
        screen = pygame.display.set_mode((800,400))
        font = pygame.font.SysFont('Arial',10)
        left_time = self.calls[0][1]
        right_time = min(self.calls[-1][1],left_time+10)
        no_more_time = self.calls[-1][1]
        calls= list(self.calls)
        surf = pygame.Surface((800,400))
        from Utils.Math.Fast import cache
        def lerp(a,b,t):
            return a * (1-t) + b * t
        def inverse_lerp(a,b,c):
            return (c - a)/(b-a)
        def map2(a,b,c,x,y):
            t= inverse_lerp(a,b,c)
            return lerp(x,y,t)

        @cache
        def get_color(s:str):
            return hash(s) & 0xFF_FF_FF
        @cache
        def render_string(s:str,color:tuple[int,int,int]|str='black'):
            return font.render(s,True,color)
            
        def draw(start_index:int):
            screen.fill('white')
            assert calls[start_index][0] == 0
            stack:list[tuple[float,str]] = [calls[start_index][1:]]
            i = start_index + 1
            
            while i < len(calls):
                cur = calls[i]
                
                if cur[0] == 0: 
                    stack.append(cur[1:])
                elif not stack:
                    print('not that bad')
                elif stack[-1][1] == cur[2]:
                    #Draw Code Here
                    height = 30
                    y = len(stack)*height
                    start_time = stack[-1][0]
                    end_time = cur[1]
                    start_x = map2(left_time,right_time,start_time,0,surf.get_width())
                    end_x = map2(left_time,right_time,end_time,0,surf.get_width())
                    d_time= (end_time-start_time)
                    t_suf = 'secs'
                    if d_time < 1:
                        d_time *= 1000
                        t_suf = 'millis'
                    # print(left_time,right_time,start_time)
                    # print((start_x,y,end_x-start_x,height))
                    pygame.draw.rect(screen,get_color(cur[2]),(start_x,y,end_x-start_x,height))
                    screen.blit(render_string(cur[2]), (start_x,y))
                    screen.blit(render_string(str(round(d_time,2))+t_suf), (start_x,y+10))
                    # End Draw Code
                    stack.pop()
                    
                else:
                    print('BAD')
                i+=1
        draw(0)
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    to_move = (right_time - left_time)  * 0.05
                    if event.key == pygame.K_LEFT:
                        dt = right_time - left_time
                        left_time -= to_move
                        if left_time < 0:
                            left_time = 0
                        right_time = left_time + dt
                        draw(0)
                    elif event.key == pygame.K_RIGHT:
                        dt = right_time - left_time
                        right_time += to_move
                        if right_time > no_more_time:
                            right_time = no_more_time
                        left_time = right_time - dt
                        draw(0)
                    elif event.key == pygame.K_UP:
                        left_time -= to_move/2
                        if left_time < 0:
                            left_time = 0
                        right_time += to_move/2
                        if right_time > no_more_time:
                            right_time = no_more_time
                        draw(0)
                    elif event.key == pygame.K_DOWN:
                        left_time += to_move/2
                        right_time -= to_move/2
                        if left_time >= right_time:
                            avg = (left_time + right_time)/2
                            left_time = avg - 0.01
                            right_time = avg + 0.01
                        draw(0) 
            # screen.blit(surf)
            pygame.display.flip()
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
