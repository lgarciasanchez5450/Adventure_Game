from typing import Generator,ParamSpec,TypeVar,Callable,Unpack,TypeVarTuple
from .Entities import entity_factory,entities,live_components,GameObject,entities_amount
from array import array
T = TypeVar('T',GameObject,GameObject,covariant=True)

from ....Utils.debug import profile


def spawnEntity(entity:type[T]) -> T:
    if entity.__name__ not in entity_factory:
        raise ValueError(f"The entity {entity.__name__} does not exist or has not been registered!")
    e = entity_factory[entity.__name__]()
    for comp,list in live_components.items():
        for c in e.__dict__.values():
            if c.__class__.__name__ == comp:
                list.append(c)
            else:
                list.append(None)
    if _resusable__uuids:
        e._uuid = _resusable__uuids.pop()
    else:
        e._uuid = entities_amount
    entities.append(e)
    return e

def destroyEntity(entity:GameObject):
    global to_kill
    if not entity._kill:
        entity._kill = True
        to_kill += 1
 
def findAllEntitiesOfType(type:type[T]) -> list[T]: 
    '''O(n) where n is amount of entities loaded'''
    return [e for e in entities[:entities_amount] if e.__class__ is type and e._kill is False]

def findAllEntitiesWithComponents(*components:type):  #TODO : profile and optimize
    '''O(n) where n is amount of entities loaded'''
    for entity in entities[:entities_amount]:
        if not entity._kill and all(entity.hasComponent(c) for c in components):
            yield entity

T2 = TypeVarTuple('T2')
def findAllComponentSets(*components:Unpack[T2]) -> Generator[tuple[*T2],None,None]: 
    '''O(n) where n is amount of entities loaded'''
    component_names:list[str] = [c.__class__.__name__ for c in components] #type: ignore
    for entity in entities[:entities_amount]:
        e_components = []
        for name in component_names:
            if (c := live_components[name][entity._uuid]) is None: break  #type: ignore
            e_components.append(c)
        else:
            yield components #type: ignore
    







### Private Engine Functions / Variables ###
to_kill = 0
CULL_PERCENT = 0.2
_resusable__uuids:array = array('B')
@profile
def _manage_killed_entities_fast(): #this is optimized to handle large amounts of entities at once by spreading work over several frames
    global entities_amount

    MAX_CULL = (to_kill * CULL_PERCENT).__ceil__()
    if to_kill == 0: return
    x = 0
    i = 0
    for i,entity in enumerate(reversed(entities[:entities_amount])):
        if entity._kill: #type: ignore
            x += 1
            if x == MAX_CULL:
                break
    pointer = entities_amount-i-1 
    deleted = 0
    while pointer != entities_amount:
        e = entities[pointer]
        if e._kill:
            _resusable__uuids.append(e._uuid)
            deleted += 1
        else:
            entities[pointer-deleted] = e
        pointer += 1
    entities_amount -= deleted


def _manage_killed_entities_slow(): #this is optimized to clean up the mess left behind by _manage_killed_entities_fast, should run periodicaly, when frame speed is considered unimportant.
    pass