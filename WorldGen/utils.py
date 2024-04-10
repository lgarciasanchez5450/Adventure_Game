from typing import Any
import numpy as np
import numpy.typing as nptyping 
from numpy._typing import _Shape

try:
    from numba import njit, prange
except ImportError:
    print('library <numba> is not installed this will significantly reduce the performance of the program.\n\
to install numba -> Open terminal -> C:\\ pip install numba')
    def njit(*args, **kwargs):
        def wrapper(func):
            return func
        return wrapper  
    prange = range

@njit(cache = True)
def paste(source:np.ndarray,dest:np.ndarray,pos:np.ndarray[Any,np.dtype[np.int32]]|tuple[int,int]):
    '''O(n) n is size of source'''
    ssx = source.shape[1]//2
    ssy = source.shape[0]//2
    for y in range(source.shape[0]):
        dest_y = pos[1] + y - ssy
        if dest_y < 0 or dest_y >= dest.shape[0]:
            continue
        for x in range(source.shape[1]):
            dest_x = pos[0] + x - ssx
            if 0 <= dest_x < dest.shape[1]:
                dest[dest_y][dest_x] = source[y][x]
    return dest

def getOnes(a:np.ndarray):
    for y,row in enumerate(a):
        for x,cell in enumerate(row):
            if cell == 1:
                yield x,y

def getOnesOffset(a:np.ndarray,pos:np.ndarray,max_shape:_Shape):
    ssx = a.shape[1]//2
    ssy = a.shape[0]//2
    for y,row in enumerate(a):
        y = y-ssy + pos[1]
        if y < 0 or y >= max_shape[0]: #index zero cause we should be passing in a <shape> value
            continue
        for x,cell in enumerate(row):
            if cell == 1:
                x = x-ssx +pos[0]
                if 0 <= x < max_shape[0]:
                    yield x,y


def fitsIn(arr1:np.ndarray,big:np.ndarray,pos:np.ndarray|tuple[int,int]):
    half_height = arr1.shape[0]//2
    half_width = arr1.shape[1]//2
    top = -half_height + pos[1]
    right = arr1.shape[1] - half_width + pos[0]
    left = -half_width + pos[0]
    bottom = arr1.shape[1] - half_height + pos[1]
    if top < 0 or left < 0: return False
    if right > big.shape[1] or bottom > big.shape[0]: return False 
    return True




def collides(test:np.ndarray,source:np.ndarray,pos:np.ndarray|tuple[int,int]):
    ssx = test.shape[1]//2
    ssy = test.shape[0]//2  
    for y in range(test.shape[0]):
        dest_y = pos[1] + y - ssy
        if dest_y < 0 or dest_y >= source.shape[0]:
            continue
        for x in range(test.shape[1]):
            dest_x = pos[0] + x - ssx
            if 0 <= dest_x < source.shape[1]:
                if test[y][x] != 0 and source[dest_y][dest_x] != 0:
                    return True
    return False


@njit(cache = True)
def hash2D(x:int,y:int):
    s = abs((x * 73856093 + 19349663)  ^  y * 83492791)
    return  ((s >> 22) ^ s) & 0xFFFFFFF



@njit(cache = True)
def random(state:nptyping.NDArray[np.uint32]):
    state[0] = state[0] * 747796405 + 2891336453
    state[1] = ((state[0] >> ((state[0] >> 28) + 4)) ^ state[0]) * 277803737
    state[1] = (state[1] >> 22) ^ state[1]
    return state[1] 
@njit(cache = True)
def randomNormalized(state:nptyping.NDArray[np.uint32]):
    state[0] = state[0] * 747796405 + 2891336453
    state[1] = ((state[0] >> ((state[0] >> 28) + 4)) ^ state[0]) * 277803737
    state[1] = (state[1] >> 22) ^ state[1]
    return state[1]  / 4294967295

state = np.zeros(2,np.uint32)

def printArray(arr:np.ndarray):
    for row in arr:
        print(f'[{" ".join((str(cell) for cell in row))}]')