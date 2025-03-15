   
#### ENTITY EFFECTS ####
#disclaimer : e - effects only affect alive entities sooo the name isn't perfect but whatever, I HAVE CONTROL HERE!!, mwuaa HA HA !!
from typing import TYPE_CHECKING
from .Constants import EntityEffects
import Application.Game.Time as Time
if TYPE_CHECKING:
    from Application.Game.general_manager import AliveEntity
__all__ = [
    'EntityEffect',
    'SuperStrength1',
    'Speed1'
]
class EntityEffect: # these effects should take care of themselves in the sense that entities should only know that they exist not whats happening to them
    __slots__ = 'name','entity','time'
    def __init__(self, name:str, entity:'AliveEntity' ) -> None:
        self.name:str = name
        self.entity = entity
        self.entity.effects.append(self)


    def update(self):
        assert hasattr(self,'time'), 'when using the default entityeffect update, <time> instance attr should be set!' 
        self.time -= Time.deltaTime
        if self.time <= 0:
            self.remove()

    
    def remove(self): ...

class SuperStrength1(EntityEffect):
    def __init__(self, entity: 'AliveEntity'):
        super().__init__(EntityEffects.EFFECT_STRENGTH_I, entity)
        self.time = 60.0
        self.entity.setExtraStatStrength(self.name,1000)


    def remove(self):
        ## Decouple the effect and the entity so they no  longer know about each other
        self.entity.removeExtraStatStrength(self.name)
        self.entity.effects.remove(self) 
        del self.entity 


class Speed1(EntityEffect):
    def __init__(self, entity: 'AliveEntity') -> None:
        super().__init__(EntityEffects.EFFECT_SPEED_I,entity)
        self.time = 60
        entity.setExtraStatSpeed(self.name,50.0)
    
    def remove(self):
        ## Decouple the effect and the entity so they no  longer know about each other
        self.entity.removeExtraStatSpeed(self.name)
        self.entity.effects.remove(self) 
        del self.entity 
