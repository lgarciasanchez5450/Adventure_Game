from typing import final
from numba import njit,prange
from math import cos, sin,pi,hypot,sqrt,atan2,floor,log2
from random import random 
import entity_manager

scalar = int|float
@njit(cache = True)
def rectangle_overlap(x1:float,x2:float,x3:float,x4:float,y1:float,y2:float,y3:float,y4:float):
	widthIsPositive = min(x3, y3) > max(x1, y1)
	heightIsPositive = min(x4, y4) > max(x2, y2)
	return (widthIsPositive and heightIsPositive)
rectangle_overlap(1,2,3,4,5,6,7,8)

def get_most_sig_bits(x:int,bits:int) -> int:
	bit_length = x.bit_length()
	output = 0
	for i in range(1,bits+1):
		if i > bit_length:
			break
		output <<= 1
		output |= (x>>(bit_length-i) ) & 1
	return output


def inclusive_range(start,stop,step):
	#yield from range(start,stop,step)
	#yield stop
	return entity_manager.inclusive_range(start,stop,step)

def abssin(x:float|int):
	return abs(sin(x))

def abscos(x:float):
	return abs(cos(x))

@njit(cache=True)
def _opposite_normalized(x,y):
	mag = sqrt(x*x+y*y)
	if mag == 0:
		return (0,0)
	return -x/mag,-y/mag


class UnInstantiable:
	'''Denoting that classes should not have instances.'''
	def __new__(cls,*args,**kwargs):
		raise RuntimeError(f"{cls} shouldn't be instantiated")

class ImplementsDraw:
	def draw(self): ...

class Vector2:
	__slots__  = ('x','y')
	def __init__(self,x,y):
		self.x:scalar = x
		self.y:scalar = y
	@final
	@classmethod
	@property
	def zero(cls):
		return Vector2(0,0)
	
	@final
	@classmethod
	@property
	def random(cls):
		'''A random Vector2 with a random distribution from [-1,1] on both x and y axis'''
		return Vector2(random()*2-1,random()*2-1)
		
	@final
	@classmethod
	@property
	def randdir(cls):
		angle = 2*pi*random()
		return Vector2(cos(angle),sin(angle))
	
	def opposite_normalized(self):
		return Vector2(*_opposite_normalized(self.x,self.y))

	def __eq__(self,__object):
		return self.x == __object.x and self.y == __object.y
	
	def __add__(self,__object):
		return Vector2(self.x + __object.x,self.y + __object.y)
	
	def __sub__(self,__object):
		return Vector2(self.x - __object.x,self.y - __object.y)
	
	def __mul__(self,__object:scalar):
		return Vector2(self.x *__object,self.y * __object)
	
	def __truediv__(self,__object:scalar):
		return Vector2(self.x / __object, self.y / __object)
	
	def __itruediv__(self,__object:scalar):
		self.x /= __object
		self.y /= __object
		return self

	def __floordiv__(self,__object:scalar):
		return Vector2(self.x // __object, self.y // __object)
	
	def dot(self,__object):
		return Vector2(self.x*__object.x,self.y*__object.y)
	
	def vector_mul(self,__object):
		return Vector2(self.x*__object.x,self.y*__object.y)
	
	def __getitem__(self,__index:int) -> scalar:
		return [self.x,self.y][__index]
	
	def __iadd__(self,__object):
		self.x += __object.x
		self.y += __object.y
		return self

	def __isub__(self,__object):
		self.x -= __object.x
		self.y -= __object.y
		return self

	def __imul__(self,__object:scalar):
		self.x *= __object
		self.y *= __object
		return self

	def __str__(self) -> str:
		return f"Vec2(x:{self.x}, y:{self.y})"	
	
	def __neg__(self):
		return Vector2(-self.x,-self.y)
	
	def inverse(self):
		return Vector2(1/self.x,1/self.y)
	
	@property
	def normalized(self):
		x,y = normalize(self.x,self.y)
		return Vector2(x,y)
	
	@property
	def isZero(self) -> bool:
		return self.x == self.y == 0
	
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
	
	def set_to(self,__object):
		self.x = __object.x
		self.y = __object.y

	def from_tuple(self,tup:tuple[scalar,scalar]):
		self.x = tup[0]
		self.y = tup[1]

	@property
	def tuple(self):
		return (self.x,self.y)
	
	@property
	def tupled_ints(self):
		return (self.x.__trunc__(),self.y.__trunc__())

	def copy(self):
		return Vector2(self.x,self.y)
	
	def rotate(self,theta:scalar):
		cs = cos(theta)
		sn = sin(theta)
		px = self.x * cs - self.y * sn
		py = self.x * sn + self.y * cs
		self.x = px
		self.y = py

	def floored(self):
		return Vector2(floor(self.x),floor(self.y))

	def get_angle(self) -> scalar:
		return atan2(self.y,self.x)

	def clamp_boxlike(self,magnitude:scalar):
		if self.x > magnitude:
			self.x = magnitude
		elif self.x < -magnitude:
			self.x  = -magnitude
		if self.y > magnitude:
			self.y = magnitude
		elif self.y < -magnitude:
			self.y = -magnitude
		return self
	


ones= Vector2(1,1)


def cap_magnitude(vector2:Vector2,mag:scalar):
	if vector2.magnitude_squared() > mag*mag:
		return vector2 * (mag / vector2.magnitude())
	return vector2.copy()
class Collider:
	__slots__ = ('x','y','width','height','bottom','top','left','right')
	def __init__(self,x,y,w,h) -> None:
		self.x:float|int = x
		self.y:float|int = y
		self.width:float|int = w
		self.height:float|int = h
		self.bottom:float|int = y+h
		self.top:float|int = y
		self.left:float|int = x
		self.right:float|int = x+w

	@classmethod
	def SpawnOnBlockCenter(cls,x:int,y:int,w:float,h:float):
		assert isinstance(x,int) and isinstance(y,int), 'x and y must be integers!'
		xPos = x+.5  - w/2
		yPos = y + .5 - h/2
		return Collider(xPos,yPos,w,h)
	
	@classmethod
	def spawnFromCenter(cls,x,y,w,h):
		xPos = x - w/2
		yPos = y - h/2
		return Collider(xPos,yPos,w,h)
	
	def move_x(self,x:float):
		self.x += x
		self.left = self.x
		self.right = self.x + self.width

	def move_y(self,y:float):
		self.y += y
		self.top = self.y
		self.bottom = self.y + self.height

	def move(self,displacement:Vector2):
		self.move_x(displacement.x)
		self.move_y(displacement.y)

	def setCenterX(self,x):
		self.x -= self.left + self.width/2  -  x
		self.left = self.x
		self.right = self.x+self.width

	def setCenterY(self,y):
		self.y -= self.top + self.height/2  -  y
		self.top = self.y
		self.bottom = self.y+self.height

	def setCenter(self,x,y):
		self.setCenterX(x)
		self.setCenterY(y)
	
	def setRight(self,right):
		self.right = right
		self.left = right-self.width
		self.x = self.left
	
	def setLeft(self,left):
		self.x = left
		self.left = left
		self.right = left + self.width

	def setBottom(self,bottom):
		self.bottom = bottom
		self.top = bottom-self.height
		self.y = self.top


	def setTop(self,top):
		self.y = top
		self.top = top
		self.bottom = top + self.height

	@property
	def size(self) -> tuple[float|int,float|int]:
		return self.width,self.height

	@property
	def centerx(self) -> float:
		return self.x + self.width/2
	
	@property
	def centery(self) -> float:
		return self.y + self.height/2
	
	@property
	def center(self) -> tuple:
		return ((self.left + self.right)/2, (self.top + self.bottom)/2)

	@property
	def topleft(self):
		return (self.left,self.top)

	@property
	def topright(self):
		return (self.right,self.top)
	
	@property
	def bottomleft(self):
		return (self.left,self.bottom)

	@property
	def bottomright(self):
		return (self.right,self.bottom)

	@centerx.setter
	def centerx(self,newVal): raise SyntaxError('This Value cannot be set!')

	@centery.setter
	def centery(self,newVal): raise SyntaxError('This Value cannot be set!')

	@center.setter
	def center(self,newVal): raise SyntaxError('This Value cannot be set!')

	@topleft.setter
	def topleft(self,newVal): raise SyntaxError('This Value cannot be set!')
	
	@topright.setter
	def topright(self,newVal): raise SyntaxError('This Value cannot be set!')
	
	@bottomleft.setter
	def bottomleft(self,newVal): raise SyntaxError('This Value cannot be set!')
	
	@bottomright.setter
	def bottomright(self,newVal): raise SyntaxError('This Value cannot be set!')
	

	def collide_collider(self,c):
		assert isinstance(c,Collider), "argument <c> must be of type 'Collider'"
		return rectangle_overlap(self.left,self.top,self.right,self.bottom,c.left,c.top,c.right,c.bottom)

	def collide_point_inclusive(self,point):
		assert isinstance(point,(tuple,list)), 'point must be a "tuple" or "list" '
		assert len(point) == 2, 'point must have a length of 2'
		x,y = point
		return self.left <= x <= self.right and self.top <= y <= self.bottom

	def collide_point_exclusive(self,point):
		assert isinstance(point,(tuple,list)), 'point must be a "tuple" or "list" '
		assert len(point) == 2, 'point must have a length of 2'
		x,y = point
		return self.left < x < self.right and self.top < y < self.bottom
		
	def __str__(self):
		return f'Collider(x: {self.x:.2f}, y: {self.y:.2f}, w: {self.width:.2}, h: {self.height:.2f})'

class Has_Collider:
	collider:Collider
import typing
T = typing.TypeVar('T')
class Array(list,typing.Generic[T]):
    @staticmethod
    def none_range(stop:int):
        a = -1
        while (a := a + 1) < stop:
            yield None
    @classmethod
    def new(cls,size:int):
        return cls(cls.none_range(size))
    
    def append(self, __object):
        return SyntaxError("Array Size cannot be changed")
    
    def remove(self, __value):
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

    def take(self,__index):
        item,self[__index] = self[__index],None
        return item

    def swap(self,__index,__object):
        item,self[__index] = self[__index],__object
        return item


def is_collider(object) -> bool:
	return isinstance(object,Collider)

def make2dlist(x,y = None):
	y = x if y is None else y
	return [[None] * x for _ in range(y)]

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

normalize(1,1)
set_mag(1,1,1)

def cache(func):
	inputs = {}
	def wrapper(*args):
		try:
			return inputs[tuple(args)]
		except:
			inputs[tuple(args)] = func(*args)
			return inputs[tuple(args)]
	return wrapper

if __name__ == '__main__':
	pass