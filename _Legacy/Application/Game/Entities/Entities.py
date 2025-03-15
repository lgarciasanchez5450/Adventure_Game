from typing import TypeVar,Literal,Callable
T = TypeVar('T')
entity_factory:dict[str,Callable[[],'GameObject']] = {}
tags:set[str] = set()

class GameObject:
    tag:str|None
    _uuid:int #set by the spawnEntity function
    _kill:bool
    __slots__ = '_kill','_uuid','tag'
    def __init__(self):
        self._kill = False
        self._uuid = -1
        self.tag = None

    def __init_subclass__(cls) -> None:
        registerEntity(cls)

    def hasComponent(self,component:type[T]) -> bool: 
        return self._hasComponent(component.__name__)
    def _hasComponent(self,name:str) -> bool: 
        return live_components[name][self._uuid] is not None
    def getComponent(self,component:type[T]) -> T: 
        comp = self._getComponent(component.__name__) 
        assert isinstance(comp,component)
        return comp#type: ignore
    def tryGetComponent(self,component:type[T]) -> T|None: 
        return self._getComponent(component.__name__) #type: ignore
    def _getComponent(self,name:str) -> object|None: 
        return live_components[name][self._uuid]
    
    def addComponent(self,component:type[T],*args) -> T|Literal[False]:
        t = live_components[component.__name__]
        if t[self._uuid] is not None: return False
        c = t[self._uuid] = component(*args)
        return c
    
    def __eq__(self,other:"GameObject"):
        return self._uuid == other._uuid



def registerEntity(factory:Callable[[],GameObject]):
    if factory.__name__ in entity_factory:
        raise SyntaxError("Cannot have two entities with the same name!")
    entity_factory[factory.__name__] = factory
    return factory

registerEntity(GameObject)

from ..Components._Component import components
live_components:dict[str,list[object|None]] = {k:[] for k in components}
del components


entities:list[GameObject] = []
entities_amount:int = 0


##### ENTITIES #####
from ..Components import Health,PlayerController,Position,Renderable,Rigidbody,Stats,Velocity,Camera as C_Camera

class DynamicEntity(GameObject):
    def __init__(self):
        self.pos = Position.Position.zero()
        self.vel = Velocity.Velocity.zero()
        self.rb = Rigidbody.Rigidbody()

class LiveEntity(DynamicEntity):
    def __init__(self) -> None:
        super().__init__()
        self.health = Health.Health(10,10)
        self.stats = Stats.Stats()

class Player(LiveEntity):
    def __init__(self) -> None:
        self.player_controller = PlayerController.PlayerController()


class Camera(GameObject):
    def __init__(self):
        self.pos = Position.Position.zero()
        self.cam = C_Camera.Camera()
    