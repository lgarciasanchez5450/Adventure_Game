from typing import final
from . import Settings
from .Constants import *
from .Game_Typing import abstractmethod,T
class Ground:
    __insts:dict[str,'Ground'] = {}
    id:int = -1
    __slots__ = 'is_solid','surface_friction'
    @abstractmethod
    @staticmethod
    def __custom_init__(inst:T) -> T: '''Initialization on the basic shared instance of the ground''';...
    
    def __new__(cls,as_new:bool = False):
        if as_new:
            return cls.__custom_init__(super(Ground,cls).__new__(cls))
        else:
            try:
                return cls.__insts[cls.__name__]
            except LookupError:
                s = cls.__insts[cls.__name__] = cls.__custom_init__((super(Ground,cls).__new__(cls)))
                assert not hasattr(s,'__dict__'), 'Ground Types must not have __dict__ attr, use __slots__ = tuple() as a class variable to fix!'
                return s

    @property
    def name(self):
        return Settings.GROUND_NAME_BY_NUMBER[self.id]

    @property
    def tex(self):
        return Settings.GROUND_TEXTURE_BY_ID[self.id]

    def __repr__(self):
        return f"Ground: {self.name}"
 
class SolidGround(Ground):
    __slots__ = ()
    def __init_subclass__(cls) -> None:   
        initial = cls.__custom_init__
        def wrapper(inst:"Ground") -> "Ground":
            nonlocal initial
            inst.is_solid = True
            return initial(inst)
        wrapper.__name__ = cls.__custom_init__.__name__
        cls.__custom_init__ = wrapper

class Invalid(Ground):
    id = GROUND_INVALID
    surface_friction = 0
    __slots__ = ()
    @staticmethod
    def __custom_init__(inst: T)  -> T:
        return inst


@final
class Stone(SolidGround):
    id = GROUND_STONE
    __slots__ = ()
    @staticmethod
    def __custom_init__(inst:'Ground') -> "Ground":
        inst.surface_friction = 10
        return inst
    
class Water(Ground):
    id = GROUND_WATER
    __slots__ = ()
    @staticmethod
    def __custom_init__(inst:'Ground') -> "Ground":
        inst.surface_friction = 2
        return inst
    
class Dirt(SolidGround):
    id = GROUND_DIRT
    __slots__ = ()
    @staticmethod
    def __custom_init__(inst:'Ground') -> "Ground":
        inst.surface_friction = 9
        return inst
    
class Grass(SolidGround):
    id = GROUND_GRASS
    __slots__ = ()
    @staticmethod
    def __custom_init__(inst: "Ground") -> "Ground":
        inst.surface_friction = 9
        return inst
    
class Sand(SolidGround):
    id = GROUND_SAND
    __slots__ = ()
    @staticmethod
    def __custom_init__(inst: "Ground") -> "Ground":
        inst.surface_friction = 7
        return inst
    
#sleep(10)
#GroundFactory = Callable[[],Ground]
#GroundRegistry:dict[int,GroundFactory] = {}
#
#def registerGround(ReturnsGround:GroundFactory,id:int,game_name:str):
#    registeringError = "Error in Registering Item: "+game_name
#    global GroundRegistry
#    if id < 0 :
#        raise RuntimeError("Block ID must be >0")
#    if id in GroundRegistry:
#        print("Cannot override a previous ground registered in GroundRegistry")
#        raise RuntimeError()
#    if id in Settings.GROUND_NAME_BY_NUMBER or game_name in Settings.GROUND_NAME_BY_NUMBER.values():
#        print("Cannot override a previous ground registered in GroundRegistry")
#        raise RuntimeError()
#    Settings.GROUND_NAME_BY_NUMBER[id] = game_name
#    #Testing if item is good to add
#    assert callable(ReturnsGround) , registeringError
#    testItem = ReturnsGround()
#    if type(testItem) is not Ground:
#        print(registeringError)
#        return
#    
#    GroundRegistry[id] = ReturnsGround
#    print('Succesfully Registered Ground ->',game_name)
#
#def getGround(id:int) -> Ground:
#    assert id in GroundRegistry, 'Invalid Ground ID: ' + str(id)
#    return GroundRegistry[id]()
#
#registerGround(lambda : Ground(GROUND_INVALID).setFriction(-1),GROUND_INVALID,'Invalid Ground')
#registerGround(lambda : Ground(GROUND_STONE).setFriction(20),GROUND_STONE,'Stone')
#registerGround(lambda : Ground(GROUND_WATER).setFriction(2),GROUND_WATER,'Water')
#registerGround(lambda : Ground(GROUND_DIRT).setFriction(9),GROUND_DIRT,'Dirt')
#registerGround(lambda : Ground(GROUND_GRASS).setFriction(9),GROUND_GRASS,'Grass')
#
#
#
#NullGround = Ground(-1)
#