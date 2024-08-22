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

class WorleyNoise:
    def __init__(self,seed:int, scale:float,i_mod:int):
        self.global_hash = hash(seed.__repr__()) # for each cell hashing
        self.scale = scale
        self.island_mod = i_mod

    def getAt(self,x:float,y:float):
        return modifier(_getAt(x*self.scale,y*self.scale,self.global_hash))

    def getArrShifted(self,xs,ys):
        return _getArr(xs,ys,self.scale,self.global_hash,self.island_mod)
    
    def getArr(self,xs,ys):
        return _getArr(xs,ys,self.scale,self.global_hash,self.island_mod)


class WorleyNoiseSimple(WorleyNoise):
    def __init__(self,seed:int, scale):
        self.global_hash = hash(seed.__repr__()) # for each cell hashing
        self.scale = scale
        self.island_mod = 15


### BEWARE ###
# There be dragons in the depths below


@njit(inline='never')
def _get_point_of_cell(x:int,y:int,global_hash):
    random.seed(hash((x,y) )^ global_hash)
    return x + random.random(), y + random.random()

@njit(inline = 'never')
def _get_surrounding_cells(x:int,y:int):
    return numpy.array(((x-1,y-1),(x,y-1),(x+1,y-1),
                        (x-1,y),  (x,y),  (x+1,y),
                        (x-1,y+1),(x,y+1),(x+1,y+1)))



@njit
def modifier(i):
    return 2**(-i*i) * i

@njit
def _getAt(x:float,y:float,global_hash):
    cell_x = floor(x)
    cell_y = floor(y)
    shortest = 999999.9
    for cx,cy in _get_surrounding_cells(cell_x,cell_y):
        px,py = _get_point_of_cell(cx,cy,global_hash)
        d = hypot(px-x,py-y)
        if d < shortest:
            shortest = d
    return shortest

@njit(parallel = True,boundscheck = False)
def _getArr(xs:numpy.ndarray,ys:numpy.ndarray,scale:float,global_hash,island_mod):
    xs = xs * scale
    ys = ys * scale
    noise = numpy.empty((ys.size, xs.size), dtype=numpy.float32)
    for y_i in prange(ys.size):
        for x_i in range(xs.size):
            shortest_sqrd = 99999999.9
            cx = floor(xs[x_i])
            cy = floor(ys[y_i])
            surrounding_cells = numpy.array(((cx-1,cy-1),(cx,cy-1),(cx+1,cy-1),
                                             (cx-1,cy),  (cx,cy),  (cx+1,cy),
                                             (cx-1,cy+1),(cx,cy+1),(cx+1,cy+1)))
            for cx,cy in surrounding_cells:
                px,py = _get_point_of_cell(cx,cy,global_hash)
                dx = px-xs[x_i]
                dy = py-ys[y_i]
                d = dx*dx + dy*dy
                if d < shortest_sqrd:
                    shortest_sqrd = d
            noise[y_i, x_i] = sqrt(shortest_sqrd)
    return modifier(noise)

if __name__ == "__main__":
    from time import perf_counter
    e = WorleyNoiseSimple(1,.01)
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
        
