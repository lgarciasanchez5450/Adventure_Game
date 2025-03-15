from math import floor
import numpy as np
from ctypes import c_int64,c_uint32
from math import sqrt, atan2,sin, tanh,exp

try:
  from numba import njit,prange,vectorize,guvectorize
except:
  print("Warning numba module not installed! This will impact performance greatly")
  def njit(*args, **kwargs):
    def wrapper(func):
      return func
    return wrapper  
  prange = range


from math import ceil,pi,cos

'''
all taken from the library opensimplex
import opensimplex
'''
STRETCH_CONSTANT2 = -0.211324865405187    # (1/Math.sqrt(2+1)-1)/2
SQUISH_CONSTANT2 = 0.366025403784439      # (Math.sqrt(2+1)-1)/2
NORM_CONSTANT2 = 40.7#47 is original

GRADIENTS2 = np.array([
    5, 2, 2, 5,
    -5, 2, -2, 5,
    5, -2, 2, -5,
    -5, -2, -2, -5,
], dtype=np.int64)
SEED = 3

def overflow(x): return c_int64(x).value


@njit
def overflow_32(x): return x & 0xFFFFFFF

@njit(cache=True)
def _extrapolate2(perm, xsb, ysb, dx, dy):
    index = perm[(perm[xsb & 0xFF] + ysb) & 0xFF] & 0x0E
    g1, g2 = GRADIENTS2[index : index + 2]
    return g1 * dx + g2 * dy

def _init(seed=SEED):
    # Have to zero fill so we can properly loop over it later
    perm = np.zeros(256, dtype=np.int64)
    source = np.arange(256)
    # Generates a proper permutation (i.e. doesn't merely perform N
    # successive pair swaps on a base array)
    seed = overflow(seed * 6364136223846793005 + 1442695040888963407)
    seed = overflow(seed * 6364136223846793005 + 1442695040888963407)
    seed = overflow(seed * 6364136223846793005 + 1442695040888963407)
    for i in range(255, -1, -1):
        seed = overflow(seed * 6364136223846793005 + 1442695040888963407)
        r = int((seed + 31) % (i + 1))
        if r < 0:
          r += i + 1
        perm[i] = source[r]
        source[r] = source[i]
    return perm
@njit(cache=True)
def _noise2(x, y, perm):
    # Place input coordinates onto grid.
    stretch_offset = (x + y) * STRETCH_CONSTANT2
    xs = x + stretch_offset
    ys = y + stretch_offset

    # Floor to get grid coordinates of rhombus (stretched square) super-cell origin.
    xsb = floor(xs)
    ysb = floor(ys)

    # Skew out to get actual coordinates of rhombus origin. We'll need these later.
    squish_offset = (xsb + ysb) * SQUISH_CONSTANT2
    xb = xsb + squish_offset
    yb = ysb + squish_offset

    # Compute grid coordinates relative to rhombus origin.
    xins = xs - xsb
    yins = ys - ysb

    # Sum those together to get a value that determines which region we're in.
    in_sum = xins + yins

    # Positions relative to origin point.
    dx0 = x - xb
    dy0 = y - yb

    value = 0

    # Contribution (1,0)
    dx1 = dx0 - 1 - SQUISH_CONSTANT2
    dy1 = dy0 - 0 - SQUISH_CONSTANT2
    attn1 = 2 - dx1 * dx1 - dy1 * dy1
    if attn1 > 0:
        attn1 *= attn1
        value += attn1 * attn1 * _extrapolate2(perm, xsb + 1, ysb + 0, dx1, dy1)

    # Contribution (0,1)
    dx2 = dx0 - 0 - SQUISH_CONSTANT2
    dy2 = dy0 - 1 - SQUISH_CONSTANT2
    attn2 = 2 - dx2 * dx2 - dy2 * dy2
    if attn2 > 0:
        attn2 *= attn2
        value += attn2 * attn2 * _extrapolate2(perm, xsb + 0, ysb + 1, dx2, dy2)

    if in_sum <= 1:  # We're inside the triangle (2-Simplex) at (0,0)
        zins = 1 - in_sum
        if zins > xins or zins > yins:  # (0,0) is one of the closest two triangular vertices
            if xins > yins:
                xsv_ext = xsb + 1
                ysv_ext = ysb - 1
                dx_ext = dx0 - 1
                dy_ext = dy0 + 1
            else:
                xsv_ext = xsb - 1
                ysv_ext = ysb + 1
                dx_ext = dx0 + 1
                dy_ext = dy0 - 1
        else:  # (1,0) and (0,1) are the closest two vertices.
            xsv_ext = xsb + 1
            ysv_ext = ysb + 1
            dx_ext = dx0 - 1 - 2 * SQUISH_CONSTANT2
            dy_ext = dy0 - 1 - 2 * SQUISH_CONSTANT2
    else:  # We're inside the triangle (2-Simplex) at (1,1)
        zins = 2 - in_sum
        if zins < xins or zins < yins:  # (0,0) is one of the closest two triangular vertices
            if xins > yins:
                xsv_ext = xsb + 2
                ysv_ext = ysb + 0
                dx_ext = dx0 - 2 - 2 * SQUISH_CONSTANT2
                dy_ext = dy0 + 0 - 2 * SQUISH_CONSTANT2
            else:
                xsv_ext = xsb + 0
                ysv_ext = ysb + 2
                dx_ext = dx0 + 0 - 2 * SQUISH_CONSTANT2
                dy_ext = dy0 - 2 - 2 * SQUISH_CONSTANT2
        else:  # (1,0) and (0,1) are the closest two vertices.
            dx_ext = dx0
            dy_ext = dy0
            xsv_ext = xsb
            ysv_ext = ysb
        xsb += 1
        ysb += 1
        dx0 = dx0 - 1 - 2 * SQUISH_CONSTANT2
        dy0 = dy0 - 1 - 2 * SQUISH_CONSTANT2

    # Contribution (0,0) or (1,1)
    attn0 = 2 - dx0 * dx0 - dy0 * dy0
    if attn0 > 0:
        attn0 *= attn0
        value += attn0 * attn0 * _extrapolate2(perm, xsb, ysb, dx0, dy0)

    # Extra Vertex
    attn_ext = 2 - dx_ext * dx_ext - dy_ext * dy_ext
    if attn_ext > 0:
        attn_ext *= attn_ext
        value += attn_ext * attn_ext * _extrapolate2(perm, xsv_ext, ysv_ext, dx_ext, dy_ext)

    return value / NORM_CONSTANT2

@njit(cache = True)
def smoothstep(x):
  return 3 * x * x - 2 * x * x * x

@njit(cache = True)
def zero_centered_smoothstep(x):
  if x < -1: return -1
  elif x > 1: return 1
  else:
    return 2 * smoothstep((x+1)/2) - 1


perm = _init(SEED)
def noise1(x):
  return _noise1(x,perm)
@njit(cache = True)
def _noise1(x,perm):
  return _noise2(x,0,perm)



def set_seed(seed):
  global SEED,perm
  SEED = seed
  perm = _init(seed)

def noise2a(xs,ys,scale):  #noise 2 array
    return _noise2a(xs * scale,ys * scale,perm)

def noise2al(xs,ys,frequencies = 1,scale = 1): #noise 2 array layered
    return _noise2al(xs,ys,frequencies,scale,perm)

def noise2ali(xs:np.ndarray,ys:np.ndarray,freq:int,scale:float,t:float,d_func,mapwidth,mapheight): #noise 2 array layered island
  map = _noise2al(xs,ys,freq,scale,perm)
  #normalize to range [0,1]
  map += 1 #
  map /= 2
  return make_island(map,xs,ys,t,d_func,mapwidth,mapheight)
@njit(cache = True)
def island(x,y,e,t,d_func,mapwidth,mapheight):
  squish = 1.5
  nx = (2*x/mapwidth - 1) * squish
  ny = (2*y/mapheight - 1) * squish
  d = d_func(nx, ny)
  if (d < 0): d = 0
  if (d > 1): d = 1
  e = lerp(e, d,t)
  return e
@njit(cache = True)
def i_point(x,y,d_func,mapwidth,mapheight):
  #nx = (2*x/mapwidth - 1) 
  #ny = (2*y/mapheight - 1) 
  nx = x/mapwidth
  ny = y/mapwidth
  #nx = zero_centered_smoothstep(x/mapwidth)
  #ny = zero_centered_smoothstep(y/mapheight)
  #should be from 

  d = d_func(nx, ny)
  

  if (d < 0): d = 0
  if (d > 1): d = 1
  #if (d > .7): d = .7 #dont completely force land for lakes to generate
  return d
@njit(cache = False, parallel = True)
def make_island(data,xs:np.ndarray,ys:np.ndarray,t,d_func,mapwidth,mapheight):
  if t == 0:return data
  result = np.zeros((xs.size,ys.size),dtype = np.double)
  for y in prange(ys.size):
    for x in prange(xs.size):
      result[y,x] = i_point(xs[x],ys[y],d_func,mapwidth,mapheight)
  if t == 1: return result
  return result * t + data * (1-t)

@njit(cache = False, fastmath = True,parallel = False)
def _noise2al(xs,ys,octaves,scale,perm): # TODO : make this run in parallel using parallel = True
  data = _noise2a(xs*scale,ys*scale,perm)
  double = 2
  total = 1
  half = .5
  for i in prange(octaves-1):
    data += _noise2a(xs*double*scale,ys*double*scale,perm) * half
    double *= 2
    total += half
    half /= 2
  data /= total
  #make island
  return data





@njit(cache = True)
def is_far(x,y,d):
  squared_dist = x*x + y*y
  return squared_dist < d*d


@njit(fastmath = True)
def blob_dist(x:float,y:float):   
  #return 1-(x*x+y*y) / 4.25 / (3 - sin(5 * atan2(y, x))) 
  return 1 - ( (x*x+y*y) * 3 / ( 3 - sin(5 * atan2(y, x)) ) ) 
@njit(cache = True)
def hypot(x:float,y:float) -> float:
  return sqrt(x*x+y*y)
@njit(cache = True)
def hypot_dist(x:float,y:float) -> float:
  return 1- sqrt(x*x+y*y)
@njit(cache = True)
def distance(x1,y1,x2,y2) -> float:
  dx = x1-x2
  dy = y1-y2
  return sqrt(dx*dx+dy*dy)
@njit(cache = True)
def square_bump_dist(x:float,y:float) -> float:
  return (1-x*x) * (1-y*y)
@njit(cache=False)
def _sigmoid_dist(x:float,vertical_squish,vertical_shift,horizontal_shift) -> float:
  return  (vertical_squish/(1.0+exp(horizontal_shift*(2*x-1)))) + (1-vertical_squish)/2 + vertical_shift
@njit(cache = False)
def sigmoid_dist(x,y):
  return _sigmoid_dist(hypot(x,y),0.64,-0.07,2.5)

   
   
@njit(cache = True)
def squared_dist(x,y):
  return 1- x*x - y*y
@njit(cache = True)
def added_dist(x,y):
  return (1-x)*(1-y)*(1+x)*(1+y)
@njit
def trig(x,y):
  return cos(x*pi/2) * cos(y*pi/2) 
@njit(cache=True)
def gauss_distance(x,y):
  return 25/11 * (exp(-(x*x+y*y))-.56)

@njit (cache = True)
def hyperboloid_dist(x,y):
  const = .1
  return  1-sqrt(x*x + y*y + const*const)
@njit (cache = True)
def euclidian_dist(x,y):
  return 1- (x*x + y*y)
@njit(cache = True)
def squircle_dist(x,y):
  return sqrt(x**4 + y**4)
@njit (cache = True)
def manhattan_dist(x,y):
  return abs(x)+abs(y)
@njit(cache = True)
def max(x,y):
  if x > y: return x
  else: return y
@njit(cache = True)
def min(x,y):
  if x < y: return x
  else: return y
@njit(cache = True)
def lerp(a, b, t):  return a * (1-t) + b * t; 
@njit(cache=True,parallel = True)
def _noise2a(x: np.ndarray, y: np.ndarray, perm: np.ndarray):
    noise = np.empty((y.size, x.size), dtype=np.double)
    for y_i in prange(y.size):
        for x_i in prange(x.size):
            noise[y_i, x_i] = _noise2(x[x_i], y[y_i], perm)
    return noise

def noise2(x,y):
    return _noise2(x,y,perm)

def noise2_layered(nx,ny,frequencies = 1, scale = 1):
    return _noise2_layered(nx,ny,frequencies,scale,perm)

@njit(cache = True,parallel = True)
def _noise2_layered(nx, ny,frequencies,scale,perm):
  mul_factor = 2
  div_factor = 1.4
  data = 0

  double = 1
  total = 0
  half = 1
  for i in range(frequencies):
    double *= mul_factor
    half /= div_factor
    total += half
    data += _noise2(nx*double*scale,ny*double*scale,perm) * half
  data /= total
  #make island
  return data



@njit(cache = True)
def normalize(x,y) -> tuple[float,float]:
  mag = hypot(x,y)
  if mag == 0: return (0,0)
  else: return (x/mag,y/mag)
@njit(cache = True)
def set_mag(x,y,mag:int|float) -> tuple[float,float]:
  if hypot(x,y) == 0: return (0,0)
  ux,uy = normalize(x,y)
  return  (ux*mag,uy*mag)

if __name__ == "__main__":
  tests = [(-1,-1), (0,0), (1,1), (-1,0)]
  answers = [0, 1, 0, 0]
  for test, ans in zip(tests,answers):
    if square_bump_dist(*test) != ans:
      raise RuntimeError(f"Tests not passed: {test} -> {square_bump_dist(*test)}: Wrong Answer")
    if round(trig(*test),11) != ans:
      raise RuntimeError(f"Tests not passed: {test} -> {trig(*test)}: Wrong Answer")
       
    


#noise2al(np.arange(5),np.arange(5),40,.1)

import random
def isValid(point,size,rad,grid):
  #print(point,size)

  if point[0] >= 0 and point[0] < size and point[1] >= 0 and point[1] < size:

    for y in range(0,rad*2+1):
      y -= rad
      y += point[1]
      if y >= size: y = size-1
      for x in range(0,rad*2+1):
        x -= rad
        x += point[0]
        if x >= size: x = size-1
        if grid[y][x] != 0:
          return False
    return True
  return False
def make2dList(xl,yl = None,default = 0) -> list:
  my_list = []
  if yl is None: yl = xl
  for y in range(yl):
    row = []
    for x in range(xl):
      row.append(default)
    my_list.append(row)
  return my_list
def GeneratePoints(radCells:int,size:int,samplesBeforeRejection = 30,max_points = 10000) -> list[tuple[float,float]]:
  #steps generate a grid so that we can store points 
  # generate a point in the middle of the grid
  #from that point 
  #makes a grid of sampleRegionSize/cellSize squared
  if radCells == 0 or radCells > size: return []
  grid = make2dList(size)
  points = []
  spawnPoints = []

  spawnPoints.append((size//2,size//2)) #middle 


  while (len(spawnPoints)) > 0:
    spawnIndex = random.randint(0,len(spawnPoints)-1)
    spawnCentre = spawnPoints[spawnIndex]
    #print(spawnCentre)
    angle = random.random() * pi * 2
    for i in range(samplesBeforeRejection):
      angle += random.random() * pi * 2
      random_mag = random.randint(radCells, 2 * radCells)
      dirx = (cos(angle) * random_mag)
      diry = (sin(angle) * random_mag)
      candidate = (int(spawnCentre[0] + dirx), int(spawnCentre[1] + diry))
      if (isValid(candidate,size,radCells,grid)):
        points.append(candidate)
        spawnPoints.append(candidate)
        grid[candidate[1]][candidate[0]] = 1
        break
    else: #for else statements only get activated if for loop terminated naturaly (eg. without use of break statement)
      spawnPoints.pop(spawnIndex)
    if len(points) > max_points:
      break
  return points

@njit(cache=True)
def scramble(x:int):
  x = overflow_32(x)
  MAX = 0xFFFFFFF
  MAGIC_NUMBER = 0b010101010101
  BIGNUM = 0xABCD123

  x1 = overflow_32(BIGNUM ^ x)
  x2 = overflow_32(BIGNUM << x) * (x+1)
  x3 = overflow_32((BIGNUM << 3) | (x * MAGIC_NUMBER) )


  y1 = overflow_32((x1 ^ x2) + x3 * MAGIC_NUMBER)
  y2 = overflow_32(x1 | x2 + x3 )
  y3 = overflow_32(x1 & x2 + x3)


  return (overflow_32(y1 << overflow_32(y2 << y3)) >> (x1%5)) & MAX
scramble(1)

class SpacedObject:
  def __init__(self,spacing:int, seed:int,dot_difficulty):
    self._map = {}
    self._perm = _init(seed)
    self._perm2 = _init(scramble(seed))
    self.spacing = spacing
    self.diagonal_spacing = spacing * (sqrt(2)/2)
    self.seed = seed
    self.to_check = [(x,y) for y in range(-2,3,1) for x in range(-2,3,1)]
    self.dot_difficulty = dot_difficulty
  def isObject(self,x,y):
    cx = x//self.diagonal_spacing
    cy = y//self.diagonal_spacing
    
    if _noise2(x*3,y*3,self._perm) > self.dot_difficulty and _noise2(y*2,x*2,self._perm2) < -self.dot_difficulty:
      for ax,ay in self.to_check:
        if (ax+cx,ay+cy) in self._map:
          if distance(*self._map[(ax+cx,ay+cy)],x2=x,y2=y) < self.spacing:
            return False

      self._map[(cx,cy)] = x,y
      return True
    return False

        

#checked = set()
#for y in range(500):
#  for x in range(500):
#    checked.add(((scramble(x*y)^scramble(y)))|(scramble(x)<<(x%2)))#

#scramble(1)
#print(len(checked))





