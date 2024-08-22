from typing import final,Callable,Any,Generic,Generator,Iterable, Callable,TypeVar
from .Fast import njit
from math import cos, sin,pi,hypot,sqrt,atan2,floor,log2,ceil,acos,tanh
from random import random,randint
from collections import deque
import numpy as np

DEBUG = True
#define inclusive_range
def inclusive_range(start:int,stop:int,step:int) -> Generator[int,None,None]: #type: ignore
	yield from range(start,stop,step)
	yield stop
try:
	import entity_manager
	inclusive_range:Callable[[int,int,int],Generator[int,None,None]] = entity_manager.inclusive_range
except:
	pass

half_sqrt_2 = (2**(1/2))/2
TO_RADIANS = pi / 180
TO_DEGREES = 180 / pi
TWO_PI = 2*pi


T = TypeVar("T")



@njit(cache = True)
def restrainMagnitude(x:float,y:float,mag:float):
	sqrM =  x*x+y*y
	if sqrM > mag * mag:
		mult = mag/sqrt(sqrM)
		x *= mult
		y *= mult
	return x,y

def getNamesOfObject(object):
	return [local for local in dir(object) if not local.startswith('__')]

@njit(cache = True)
def randomNudge(x:float,y:float,nudgeMag:float): #this random nudge prefers smaller nudges than bigger ones
	#techincally it will nudge it more in the diagonal more than horiztonal since the nudge values are not normalized
	mag = sqrt(x*x+y*y)
	nudgeX = 2*random()-1
	nudgeY = 2*random()-1
	nudgeX, nudgeY = restrainMagnitude(nudgeX,nudgeY,1)
	x += nudgeMag * nudgeX
	y += nudgeMag * nudgeY
	return  set_mag(x,y,mag)
	

def getMostSigBits(x:int,bits:int) -> int:
	return x >> max(0,x.bit_length() - bits)

def serialIter(*iters:Iterable):
	for iter in iters:
		yield from iter



class Vector2Int:
	__slots__  = 'x','y'
	def __init__(self,x:int,y:int):
		self.x = x
		self.y = y

	@final
	@classmethod
	def zero(cls):
		return Vector2Int(0,0)
	
	def __eq__(self,__object: "Vector2Int"):
		return self.x == __object.x and self.y == __object.y
	
	def __add__(self,__object: "Vector2Int"):
		return Vector2Int(self.x + __object.x,self.y + __object.y)
	
	def __sub__(self,__object: "Vector2Int"):
		return Vector2Int(self.x - __object.x,self.y - __object.y)
	
	def __mul__(self,__object:int):
		return Vector2Int(self.x *__object,self.y * __object)
	
	def __rmul__(self,__object:int):
		return Vector2Int(self.x *__object,self.y * __object)
	
	def __itruediv__(self,__object:int):
		self.x /= __object
		self.y /= __object
		return self

	def __floordiv__(self,__object:int):
		return Vector2Int(self.x // __object, self.y // __object)
	
	def moved_by(self,x:int,y:int):
		return Vector2Int(self.x + x, self.y + y)
	
	def __matmul__(self,__object: "Vector2Int"):
		return Vector2Int(self.x*__object.x,self.y*__object.y)
	
	def __getitem__(self,__index:int) -> int:
		return [self.x,self.y][__index]
	
	def __iadd__(self,__object: "Vector2Int"):
		self.x += __object.x
		self.y += __object.y
		return self

	def __isub__(self,__object: "Vector2Int"):
		self.x -= __object.x
		self.y -= __object.y
		return self

	def __imul__(self,__object:int):
		self.x *= __object
		self.y *= __object
		return self

	def __str__(self) -> str:
		return f"Vec2Int(x:{self.x}, y:{self.y})"	
	
	def __neg__(self):
		return Vector2Int(-self.x,-self.y)

	
	def magnitude_squared(self):
		return self.x*self.x+self.y*self.y
	
	def magnitude(self):
		return sqrt(self.x*self.x + self.y * self.y)
	
	def reset(self):
		'''Reset each axis to 0'''
		self.x = 0
		self.y = 0

	def __bool__(self):
		return (self.x or self.y).__bool__()
	
	def __iter__(self):
		yield self.x
		yield self.y
	
	def set_to(self,__object:'Vector2Int'):
		self.x = __object.x
		self.y = __object.y

	@classmethod
	def newFromTuple(cls,tup:tuple[int,int]):
		return Vector2Int(tup[0],tup[1])
	def from_tuple(self,tup:tuple[int,int]):
		self.x = tup[0]
		self.y = tup[1]

	@property
	def tuple(self):
		return (self.x,self.y)

	def copy(self):
		return Vector2Int(self.x,self.y)



class Array(list,Generic[T]):
	@staticmethod
	def none_range(stop:int):
		a = -1
		while (a := a + 1) < stop:
			yield None
	@classmethod
	def new(cls,size:int):
		return cls(cls.none_range(size))
	
	def __getitem__(self,index:int) -> T|None:
		return super().__getitem__(index)
	def append(self, __object):
		return SyntaxError("Array Size cannot be changed")
	
	def insert(self, __index, __object):
		return SyntaxError("Array Size cannot be changed")

	def clear(self):
		return SyntaxError("Array Size cannot be changed")
	
	def extend(self, __iterable):
		return SyntaxError("Array Size cannot be changed")

	def pop(self, __index = -1):
		return SyntaxError("Array Size cannot be changed")

	def iadd(self,__object):
		return SyntaxError("Array Size cannot be changed")

	def remove(self,__index):
		'''Set a certain Index to None'''
		self[__index] = None

	def take(self,__index):
		item,self[__index] = self[__index],None
		return item

	def swap(self,__index,__object):
		item,self[__index] = self[__index],__object
		return item

	def swapIndices(self,__index1:int, __index2:int):
		self[__index1],self[__index2] = self[__index2],self[__index1]

class Counter(Generic[T]):
	__slots__ = 'obj','a','b'
	def __init__(self,obj1:T,a:float = 0.0,):
		self.obj = obj1
		self.a = a
		self.b = 0

	def __iter__(self):
		yield self.obj
		yield self.a
		yield self.b

	def __getitem__(self,__index:int):
		assert __index in (0,1), 'Counter only supports 0 and 1 as indexes'
		return self.b if __index else self.a


def make2dlist(x:int,y:int|None = None) -> tuple[list[None],...]:
	y = x if y is None else y
	return tuple([None]*x for _ in range(y))

@njit(cache = True)
def normalize(x,y) -> tuple[float,float]:
	mag = hypot(x,y)
	if mag == 0: return (0,0)
	else: return (x/mag,y/mag)

@njit(cache = True)
def set_mag(x,y,mag:int|float) -> tuple[float,float]:
	if x*x+y*y == 0: return (0,0)
	ux,uy = normalize(x,y)

	return  (ux*mag,uy*mag)




@njit
def rgb_to_hsv(r,g,b): 
	M = max(r, g, b)
	m = min(r, g, b)

	#And then V and S are defined by the equations

	V = M/255
	S = 1 - m/M  if M > 0 else 0

	#As in the HSI and HSL color schemes, the hue H is defined by the equations
	d = sqrt(r*r+g*g+b*b-r*g-r*b-g*b)
	H = acos((r - g/2 - b/2)/d)  if g >= b else pi - acos( (r - g/2 - b/2)/d)  
	return H/pi,S,V

@njit
def hsv_to_rgb(h,s,v): 
	h *= 360
	M = 255*v
	m = M*(1-s)
	#Now compute another number, z, defined by the equation
	z = (M-m)*(1-abs((h/60)%2-1))
	#Now you can compute R, G, and B according to the angle measure of H. There are six cases. 
	R,G,B = 0,0,0
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
	return R,G,B

