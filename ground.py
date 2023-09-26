from typing import Callable, TypeVar
from sys import intern
from Constants import *
import Settings
class Ground:
   
    __slots__ = ('id','is_solid','surface_friction')
    def __init__(self,id:int):
        self.id = id
        self.is_solid = True
        self.surface_friction = 9 #kinetic friction coefficient

    @property
    def name(self):
        return Settings.GROUND_NAME_BY_NUMBER[self.id]

    @property
    def tex(self):
        return self.name+'.png'

    def setFriction(self,friction:float):
        self.surface_friction = friction
        return self
    def setIsSolid(self,isSolid:bool):
        self.is_solid = isSolid
        return self
    

    
    def __repr__(self):
        return f"Ground: {self.name}, "
GroundFactory = Callable[[],Ground]
GroundRegistry:dict[int,GroundFactory] = {}

def registerGround(ReturnsGround:GroundFactory,id:int,game_name:str):
    registeringError = "Error in Registering Item: "+game_name
    global GroundRegistry
    if id <= 0 :
        raise RuntimeError("Block ID must be >0")
    if id in GroundRegistry:
        print("Cannot override a previous ground registered in GroundRegistry")
        raise RuntimeError()
    if id in Settings.GROUND_NAME_BY_NUMBER or game_name in Settings.GROUND_NAME_BY_NUMBER.values():
        print("Cannot override a previous ground registered in GroundRegistry")
        raise RuntimeError()
    Settings.GROUND_NAME_BY_NUMBER[id] = game_name
    #Testing if item is good to add
    if not callable(ReturnsGround):
        print(registeringError)
        return
    testItem = ReturnsGround()
    if type(testItem) is not Ground:
        print(registeringError)
        return
    
    GroundRegistry[id] = ReturnsGround
    print('Succesfully Registered Ground ->',game_name)

def getGround(id:int) -> Ground:
    if id not in GroundRegistry:
        raise RuntimeError()
    return GroundRegistry[id]()

registerGround(lambda : Ground(GROUND_STONE).setFriction(20),GROUND_STONE,'Stone')
registerGround(lambda : Ground(GROUND_WATER).setFriction(2),GROUND_WATER,'Water')
registerGround(lambda : Ground(GROUND_DIRT).setFriction(9),GROUND_DIRT,'Dirt')
registerGround(lambda : Ground(GROUND_GRASS).setFriction(9),GROUND_GRASS,'Grass')



NullGround = Ground(-1)
