import numpy
import random
from math import floor , hypot, sqrt


__all__ = [
    'modifier',
    'getAt',
    'getArr',
    'getArr2',
    'njit',
    'prange'
]

from ..Math.Fast import njit, prange
    
### BEWARE ###
# There be dragons in the depths below

@njit
def _get_point_of_cell_two(x:int,y:int,global_hash:int) -> tuple[float,float]:
    x_constraint = 1.5
    y_constraint = 1.5
    random.seed(hash((x,y)) ^ global_hash) 
    return x + 0.5 + (random.random()-0.5)/x_constraint, y + 0.5 + (random.random()-0.5)/y_constraint

@njit(inline='never')
def _get_point_of_cell(x:int,y:int,global_hash):
    random.seed(hash((x,y) )^ global_hash)
    return x + random.random(), y + random.random()

@njit(inline = 'never')
def _get_surrounding_cells(x:int,y:int):
    return numpy.array(((x-1,y-1),(x,y-1),(x+1,y-1),
                        (x-1,y),  (x,y),  (x+1,y),
                        (x-1,y+1),(x,y+1),(x+1,y+1)))



@njit(cache=True)
def modifier(i):
    val = (1-i*i)
    return val * val 


@njit
def getAt(x:float,y:float,global_hash:int):
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
def getArr(xs:numpy.ndarray,ys:numpy.ndarray,scale:float,global_hash,island_mod):
    xs = xs * scale
    ys = ys * scale
    noise = numpy.empty((ys.size, xs.size), dtype=numpy.float32)
    for y_i in prange(ys.size):
        for x_i in range(xs.size):
            shortest_sqrd = 999.9
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

@njit(parallel = True)
def getArr2(xs:numpy.ndarray,ys:numpy.ndarray,scale:float,global_hash):
    xs = xs * scale  
    ys = ys * scale
    noise = numpy.empty((ys.size, xs.size), dtype=numpy.float32)
    for y_i in prange(ys.size):
        for x_i in range(xs.size):
            shortest_sqrd = 999.9
            cx = floor(xs[x_i])
            cy = floor(ys[y_i])
            surrounding_cells = numpy.array(((cx-1,cy-1),(cx,cy-1),(cx+1,cy-1),
                                             (cx-1,cy),  (cx,cy),  (cx+1,cy),
                                             (cx-1,cy+1),(cx,cy+1),(cx+1,cy+1)))
            for cx,cy in surrounding_cells:
                px,py = _get_point_of_cell_two(cx,cy,global_hash)
                dx = px-xs[x_i]
                dy = py-ys[y_i]
                d = dx*dx + dy*dy
                if d < shortest_sqrd:
                    shortest_sqrd = d
            noise[y_i, x_i] = sqrt(shortest_sqrd)
    return modifier(noise)

