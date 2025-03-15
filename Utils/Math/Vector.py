from typing import final
from random import random
from math import atan2
from math import sin
from math import cos
from math import pi

class Vector2:
	__slots__  = 'x','y'
	def __init__(self,x:float,y:float):
		self.x = x
		self.y = y
	@final
	@classmethod
	def zero(cls):
		return cls(0.0,0.0)
	
	@final
	@classmethod
	def random(cls):
		'''A random Vector2 with a random distribution from [-1,1] on both x and y axis'''
		return cls(random()*2-1,random()*2-1)
		
	@final
	@classmethod
	def randdir(cls):
		'''Random Unit Vector'''
		angle = 2*pi*random()
		return cls(cos(angle),sin(angle))
	


	def __eq__(self,__object: "Vector2"):
		return self.x == __object.x and self.y == __object.y
	
	def __add__(self,__object: "Vector2"):
		return self.__class__(self.x + __object.x,self.y + __object.y)
	
	def __sub__(self,__object: "Vector2"):
		return self.__class__(self.x - __object.x,self.y - __object.y)
	
	def __mul__(self,__object: float):
		return self.__class__(self.x *__object,self.y * __object)
	
	def __rmul__(self,__object:float):
		return self.__class__(self.x *__object,self.y * __object)

	def __truediv__(self,__object:float):
		return self.__class__(self.x / __object, self.y / __object)
	
	def __itruediv__(self,__object:float):
		self.x /= __object
		self.y /= __object
		return self

	def __floordiv__(self,__object:float):
		return self.__class__(self.x // __object, self.y // __object)
	
	def moved_by(self,x:float,y:float):
		return self.__class__(self.x + x, self.y + y)

	def dot(self,__object: "Vector2"):
		return self.x*__object.x + self.y*__object.y
	
	def __matmul__(self,__object: "Vector2"):
		return self.__class__(self.x*__object.x,self.y*__object.y)
	
	def __imatmul__(self,__object: "Vector2"):
		self.x *= __object.x
		self.y *= __object.y
		return self
	
	def __getitem__(self,__index:int) -> float:
		return [self.x,self.y][__index]
	
	def __iadd__(self,__object: "Vector2"):
		self.x += __object.x
		self.y += __object.y
		return self

	def __isub__(self,__object: "Vector2"):
		self.x -= __object.x
		self.y -= __object.y
		return self

	def __imul__(self,__object:float):
		self.x *= __object
		self.y *= __object
		return self

	def __str__(self) -> str:
		return f"Vec2(x:{self.x}, y:{self.y})"	
	
	def __neg__(self):
		return self.__class__(-self.x,-self.y)
	
	@property
	def inverse(self):
		return self.__class__(1/self.x,1/self.y)
	
	@property
	def normalized(self):
		if not (self.x or self.y): return self.__class__.zero()
		m = self.magnitude()
		return self.__class__(self.x/m,self.y/m)
	
	def magnitude_squared(self):
		return self.x*self.x+self.y*self.y
	
	def magnitude(self):
		return (self.x*self.x + self.y * self.y)**0.5
	
	def reset(self):
		'''Reset each axis to 0'''
		self.x = 0.0
		self.y = 0.0

	def __bool__(self):
		return (self.x or self.y).__bool__()
	

	def __iter__(self):
		yield self.x
		yield self.y
	
	def setFrom(self,__object:'Vector2'):
		self.x = __object.x
		self.y = __object.y

	@classmethod
	def newFromTuple(cls,tup:tuple[float,float]):
		return cls(tup[0],tup[1])

	def fromTuple(self,tup:tuple[float,float]):
		self.x = tup[0]
		self.y = tup[1]

	@property
	def tuple(self):
		return (self.x,self.y)
	
	@property
	def tuple_ints(self):
		return (self.x.__trunc__(),self.y.__trunc__())

	def copy(self):
		return self.__class__(self.x,self.y)
	
	def rotate(self,theta:float):
		cs = cos(theta)
		sn = sin(theta)
		px = self.x * cs - self.y * sn
		py = self.x * sn + self.y * cs
		self.x = px
		self.y = py

	def floored(self):
		return self.__class__(self.x.__floor__(),self.y.__floor__())

	def angle(self) -> float:
		return atan2(self.y,self.x)

	def clamp_boxlike(self,magnitude:float):
		if self.x > magnitude:
			self.x = magnitude
		elif self.x < -magnitude:
			self.x  = -magnitude
		if self.y > magnitude:
			self.y = magnitude
		elif self.y < -magnitude:
			self.y = -magnitude
		return self
		
	def asMagnitudeOf(self,other:float) -> 'Vector2':
		m = self.magnitude()
		return self.__class__(self.x * other/m, self.y * other/m)
	
	def setMagnitude(self,other:float):
		m = self.magnitude()
		if m == 0: return self
		self.x *= other / m
		self.y *= other / m
		return self

ones = Vector2(1,1)

