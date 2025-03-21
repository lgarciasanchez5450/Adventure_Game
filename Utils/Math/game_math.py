from typing import final,Callable,Any,Generic,Generator,Iterable, Callable,TypeVar
from .Fast import njit
from math import cos, sin,pi,hypot,sqrt,atan2,floor,log2,ceil,acos,tanh,exp
from random import random,randint
from collections import deque
import numpy as np
T = TypeVar('T')
DEBUG = True
#define inclusive_range
def inclusive_range(start:int,stop:int,step:int) -> Generator[int,None,None]: #type: ignore
	yield from range(start,stop,step)
	yield stop

try:
	import entity_manager2  #type: ignore
	inclusive_range:Callable[[int,int,int],Generator[int,None,None]] = entity_manager2.inclusive_range

except:
	print('Entity Manager Module has not been compiled, defaulting back to pure python, this will slow down physics.')
def collide_chunks(x1:float,y1:float,z1:float,x2:float,y2:float,z2:float,chunk_size:int): # type: ignore[same-name]
	cx1 = (round(x1,4) / chunk_size).__floor__()
	cy1 = (round(y1,4) / chunk_size).__floor__()
	cz1 = (round(z1,4) / chunk_size).__floor__()
	cx2 = (round(x2,4) / chunk_size).__ceil__()
	cy2 = (round(y2,4) / chunk_size).__ceil__()
	cz2 = (round(z2,4) / chunk_size).__ceil__()
	return[(x,y,z) for x in range(cx1,cx2,1) for z in range(cz1,cz2,1) for y in range(cy1,cy2,1)]
try:
	raise ModuleNotFoundError()
	import entity_manager2 #type: ignore
	collide_chunks:Callable[[float,float,float,float,float,float,int],tuple[tuple[int,int,int],...]] = entity_manager2.collide_chunks #type: ignore
except (ModuleNotFoundError or ImportError) as err:
	print('Error Importing entity_manager2')

	

def expDecay(a:T,b:T,decay:float,dt:float) -> T:
	'''Has the unique property that repeated calls in the pattern of 
	 >>> a = 0
	 >>> b = 100
	 >>> decay = 1 #Number representing after one second what a would be 
	 >>> for _ in range(10):
	 >>>   a = expDecay(a,b,decay,0.1)
	 >>> a
	 >>> 63.212055882855786
	 >>> a = 0
	 >>> for _ in range(20):
	 >>>   a = expDecay(a,b,decay,0.05)
	 >>> a
	 >>> 63.212055882855786 #same as previously
	This makes this function usefull for lerp smooth following with framerate independance
	'''
	return 	b+(a-b)*exp(-decay*dt) #type: ignore


def smoothFollow(a:float,b:float,decay:float,dt:float,close_threshold:float) -> float:
	if abs(a-b) < close_threshold:
		return b
	return expDecay(a,b,decay,dt)




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
	

def getMostSigBits(x:int,n:int) -> int:
	'''Get n most significant bits of x '''
	return x >> max(0,x.bit_length() - n)

def serialIter(*iters:Iterable):
	for iter in iters:
		yield from iter

@njit
def manhattan_distance(x1,y1,x2,y2):
	return abs(x1-x2)+abs(y1-y2)


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
	return tuple([[None]*x for _ in range(y)])

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

