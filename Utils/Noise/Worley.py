try:
    from numba import njit,prange
except ImportError:
    def njit(*args, **kwargs):
        def wrapper(func):
            return func
        return wrapper  
    prange = range

from math import floor,hypot, sqrt
import numpy
import random
try:
    from .WorleyUtils import modifier,getAt,getArr,getArr2
except:
    from WorleyUtils import *

class WorleyNoise:
    def __init__(self,seed:int, scale:float,i_mod:int):
        self.global_hash = hash(seed.__repr__()) # for each cell hashing
        self.scale = scale
        self.island_mod = i_mod

    def getAt(self,x:float,y:float):
        return modifier(getAt(x*self.scale,y*self.scale,self.global_hash))

    def getArrShifted(self,xs,ys):
        return getArr(xs,ys,self.scale,self.global_hash,self.island_mod)
    
    def getArr(self,xs,ys):
        return getArr(xs,ys,self.scale,self.global_hash,self.island_mod)


class WorleyNoiseSimple(WorleyNoise):
    def __init__(self,seed:int, scale):
        self.global_hash = hash(seed.__repr__()) # for each cell hashing
        self.scale = scale
        self.island_mod = 15

class WorleyNoiseSmooth(WorleyNoise):
    def __init__(self, seed: int, scale: float):
        self.global_hash = hash(seed.__repr__()) # for each cell hashing
        self.scale = scale

    def getAt(self, x: float, y: float):
        raise NotImplementedError()
        
    def getArr(self, xs, ys):
        return getArr2(xs,ys,self.scale,self.global_hash)

    def getArrShifted(self, xs, ys):
        return self.getArr(xs,ys)


if __name__ == "__main__":
    from time import perf_counter
    e = WorleyNoiseSmooth(1,.01)
    e.getArr(numpy.arange(10),numpy.arange(10))
    import pygame
    
    xs = numpy.arange(1000)
    ys = numpy.arange(1000)
    s = pygame.display.set_mode((1000,1000))
    for y, row in enumerate(e.getArr(xs,ys)):
        for x, h in enumerate(row):
            s.set_at((x,y),(h*255,h*255,h*255))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        
