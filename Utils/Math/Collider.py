from .Vector import Vector2
from numba import njit

class Collider:
	__slots__ = 'x','y','width','height','bottom','top','left','right'
	def __init__(self,x:float,y:float,w:float,h:float) -> None:
		self.width:float = w
		self.height:float = h
		self.bottom:float = y+h
		self.top:float = y
		self.left:float = x
		self.right:float = x+w

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
		self.left += x
		self.right = self.left + self.width

	def move_y(self,y:float):
		self.top += y
		self.bottom = self.top + self.height

	def move(self,displacement:Vector2):
		self.move_x(displacement.x)
		self.move_y(displacement.y)

	def setCenterX(self,x):
		self.left -= self.left + self.width/2  -  x
		self.right = self.left+self.width

	def setCenterY(self,y):
		self.top -= self.top + self.height/2  -  y
		self.bottom = self.top+self.height

	def setCenter(self,x:float,y:float):
		self.setCenterX(x)
		self.setCenterY(y)
	
	def setRight(self,right:float):
		self.right = right
		self.left = right-self.width
	
	def setLeft(self,left:float):
		self.left = left
		self.right = left + self.width

	def setBottom(self,bottom:float):
		self.bottom = bottom
		self.top = bottom-self.height
		self.top = self.top


	def setTop(self,top:float):
		self.top = top
		self.bottom = top + self.height

	@property
	def size(self) -> tuple[float,float]:
		return self.width,self.height
	
	def get_size(self) -> Vector2:
		return Vector2(self.width,self.height)

	@property
	def centerx(self) -> float:
		return self.left + self.width/2
	
	@property
	def centery(self) -> float:
		return self.top + self.height/2
	
	@property
	def center(self) -> tuple[float,float]:
		return (self.centerx,self.centery)

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
	def centerx(self,newVal:float): 
		self.left = newVal - self.width/2
		self.right = self.left + self.width

	@centery.setter
	def centery(self,newVal:float): 
		self.top =  newVal - self.height/2
		self.bottom = self.top + self.height

	@center.setter
	def center(self,newVal:tuple[float,float]):
		self.centerx = newVal[0]
		self.centery = newVal[1]
		 
	@topleft.setter
	def topleft(self,newVal): raise SyntaxError('This Value cannot be set!')
	
	@topright.setter
	def topright(self,newVal): raise SyntaxError('This Value cannot be set!')
	
	@bottomleft.setter
	def bottomleft(self,newVal): raise SyntaxError('This Value cannot be set!')
	
	@bottomright.setter
	def bottomright(self,newVal): raise SyntaxError('This Value cannot be set!')
	

	def collide_collider(self,c:'Collider'):
		return _rect_overlap(self.left,self.top,self.right,self.bottom,c.left,c.top,c.right,c.bottom)

	def collide_point_inclusive(self,point:tuple[float,float]|Vector2):
		x,y = point
		return self.left <= x <= self.right and self.top <= y <= self.bottom

	def collide_point_exclusive(self,point:tuple[float,float]):
		x,y = point
		return self.left < x < self.right and self.top < y < self.bottom
		
	def __str__(self):
		return f'Collider(x: {self.left:.3f}, y: {self.top:.3f}, w: {self.width:.3f}, h: {self.height:.3f})'


## Speedups ##

@njit
def _rect_overlap(x1:float,x2:float,x3:float,x4:float,y1:float,y2:float,y3:float,y4:float):
    return (min(x3, y3) > max(x1, y1)) and (min(x4, y4) > max(x2, y2))