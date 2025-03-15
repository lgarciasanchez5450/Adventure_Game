from .Vector import Vector2
from numba import njit
import glm
class Collider:
	__slots__ = 'c','s'
	def __init__(self,position:glm.vec3,size:tuple[float,float,float]|glm.vec3) -> None:
		self.c = position
		self.s = glm.vec3(size)
		
	
	def move_x(self,x:float):
		self.c.x += x
	def move_y(self,y:float):
		self.c.y += y
	def move_z(self,z:float):
		self.c.z += z
	def move(self,displacement:glm.vec3):
		self.c += displacement

	def setCenterX(self,x):
		self.c.x = x
	def setCenterY(self,y):
		self.c.y = y
	def setCenterZ(self,z):
		self.c.z = z
	def setCenter(self,x:float,y:float,z:float):
		self.c.xyz = x,y,z
	
	def setXPositive(self,right:float):
		self.c.x = right - self.s.x/2
	def setXNegative(self,left:float):
		self.c.x = left + self.s.x/2
	def setYPositive(self,bottom:float):
		self.c.y = bottom - self.s.y/2
	def setYNegative(self,top:float):
		self.c.y = top + self.s.y/2
	def setZPositive(self,z:float):
		self.c.z = z - self.s.z/2
	def setZNegative(self,z:float):
		self.c.z = z + self.s.z/2

	@property
	def x_positive(self):
		return self.c.x + self.s.x/2
	@property
	def x_negative(self):
		assert self.s.x > 0
		return self.c.x - self.s.x/2
	@property
	def y_positive(self):
		return self.c.y + self.s.y/2
	@property
	def y_negative(self):
		assert self.s.y > 0
		return self.c.y - self.s.y/2
	@property
	def z_positive(self):
		return self.c.z + self.s.z/2
	@property
	def z_negative(self):
		assert self.s.z > 0

		return self.c.z - self.s.z/2

	
	@property
	def size(self):
		return self.s.to_tuple()

	@property
	def centerx(self) -> float:
		return self.c.x
	
	@property
	def centery(self) -> float:
		return self.c.y
	
	@property
	def centerz(self) -> float:
		return self.c.z
	
	@property
	def center(self) -> tuple[float,float,float]:
		return self.c.to_tuple()

	@centerx.setter
	def centerx(self,newVal:float): 
		self.setCenterX(newVal)

	@centery.setter
	def centery(self,newVal:float): 
		self.setCenterY(newVal)

	@centerz.setter
	def centerz(self,newVal:float): 
		self.setCenterZ(newVal)

	@center.setter
	def center(self,newVal:tuple[float,float,float]|glm.vec3):
		self.setCenter(*newVal)
		 


	def collide_collider(self,c:'Collider'):
		dist = self.c-c.c
		size = self.s + c.s
		return (-size.x < dist.x < size.x) and (-size.y < dist.y < size.y) and (-size.z < dist.z < size.z)

	def collide_point_inclusive(self,point:tuple[float,float,float]|glm.vec3):
		dist = self.c-point
		size = self.s
		return (-size.x < dist.x < size.x) and (-size.y < dist.y < size.y) and (-size.z < dist.z < size.z)

	def collide_point_exclusive(self,point:tuple[float,float,float]|glm.vec3):
		dist = self.c-point
		size = self.s
		return (-size.x <= dist.x <= size.x) and (-size.y <= dist.y <= size.y) and (-size.z < dist.z < size.z)
		
	def __str__(self):
		return f'Collider(c:{self.c.to_tuple()},s:{self.s.to_tuple()})'


	def copy(self):
		return Collider(glm.vec3(self.c),self.s)