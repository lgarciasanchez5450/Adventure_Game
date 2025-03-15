from typing import Optional, final, TYPE_CHECKING
from .. import Textures
from ..Utils.Math.Vector import Vector2
from ..Utils.Math.game_math import randomNudge
from . import Camera
from . import InputGame as Input
from .Constants import *
from .GameScreen import Animation
from .Game_Typing import abstractmethod
import pygame
from pygame import Surface
from Application.Game.Inventory import UniversalInventory
import Application.Game.Settings as Settings
import Application.Game.Time as Time
from math import tanh
from Application.Game.EntityEffects import *
if TYPE_CHECKING:
    from Application.Game.general_manager import Arrow, ArrowExplosive, Bunny, Entity


__all__ = [
    'Item',
    'DivineBow',
    'Bow',
    'BunnyEgg',
    'StrengthPotion',
    'ItemArrow'
]



#### ITEM STATS ####
class ArmourStats:
    wearable:bool = True
    __slots__ = 'type','defense'
    def __init__(self,type:str,defense:int) -> None:
        self.type = type
        self.defense = defense

class DurabilityStats:
    breakable = True
    __slots__ = 'max_durability','durability'
    def __init__(self,max_durability:int,durability:int):
        self.max_durability = max_durability
        self.durability = durability

    def remove_durability(self,amount:int) -> bool:
        self.durability -= amount
        if self.durability <= 0:
            self.durability = 0
            return True
        return False


        


#### ITEMS ####
class Item:
    bow_shootable = False #if this is true then there MUST be a instance variable named <projectile> which can be instantiated to make an entity
    crossbow_shootable = False
    base_projectile:str #MUST be defined when ((bow_shootable || crossbow_shootable) == True)
    entity_loaded = None
    places_block = None
    lore:str = ''
    description:str = ''

    def __init_subclass__(cls) -> None:
        assert isinstance(cls.lore,str)
        assert isinstance(cls.description,str)
        if cls.bow_shootable or cls.crossbow_shootable:
            assert hasattr(cls,'base_projectile'), f'Item {cls.__name__} must define a base_projectile as it is marked as shootable by a bow or crossbow'
            assert cls.base_projectile in Settings.SPAWNABLE_ENTITIES, f' Item {cls.__name__}\'s base_projectile ({cls.base_projectile}) is not found in SPAWNABLE ENTITIES!'

    
    def setCount(self,count:int):
        assert count <= self.max_stack_count
        self.count = count
        return self
    
    __slots__ = 'tag', 'name',  'count', 'durability_stats', 'armour_stats', 'damage', 'mining_speed', 'fps', 'animation','frames','inventory'
    def __init__(self,tag:str,frames:tuple[Surface,...]|None = None):
        self.tag = tag #all the same types of items should have the same tag
        self.name = Settings.ITEM_BASE_NAME_FROM_TAG.get(tag,tag) # display name should start as default tag
        self.count = 1
        self.durability_stats:DurabilityStats|None = None
        self.armour_stats:ArmourStats|None = None
        self.damage:int = 0 
        self.mining_speed:int = 0 
        if frames:
            self.frames = frames
        else:
            self.frames:tuple[pygame.Surface,...]  = Textures.items.get(self.tag,(Textures.NULL,))# at most 60 frames 
        self.inventory:UniversalInventory
        self.animation = Animation.SimpleAnimation(Camera.CSurface(Textures.NULL,Vector2.zero(),(0,0)),0,self.frames)

    @property
    def max_stack_count(self):
        return Settings.STACK_COUNT_BY_TAG.get(self.tag,DEFAULT_ITEM_MAX_STACK)

    def getAttack(self) -> int:
        return self.damage
    @property
    def armour_type(self) -> str|None:
        return None if self.armour_stats is None else self.armour_stats.type
    
    #this method is called every frame during in which is in use
    def duringUse(self, inventory: UniversalInventory) -> None: ...

    #this method is called on right click down
    def startUse(self,inventory:UniversalInventory) -> None: ...
    
    #This function will also be called when the item stops being in main hand or on right click up
    def stopUse(self,inventory:UniversalInventory) -> None: ...

    def takeOne(self):
        assert self.count > 0, 'cannot takeOne from an item that is already zero '
        self.count -=1 
        return self.copy()

    def copy(self):
        try: 
            return self.__class__() #type: ignore
        except:
            raise RuntimeError('Cannot Create a copy of '+self.__class__.__name__)
    
    def stackCompatible(self,other :Optional["Item"]) -> bool:
        '''
        Returns whether the items can possibly be stacked
        with no regard if the item is fully stacked
        '''
        if other is None: return False
        assert isinstance(other,Item) 
        return self.tag is other.tag and self.name == other.name
    
    def __repr__(self) -> str:
        if DEBUG: print('This should not be called!!')
        return self.__class__.__name__ + ": " + self.tag +": " + self.name

    def __eq__(self,other):
        raise RuntimeError("For what purpose?!?!")

class DrinkableItem(Item):
    DRINKING = 0
    NOT_DRINKING = 1
    IN_BETWEEN_DRINKS = 2
    drinking_delay:float = 0.05 #how many seconds should be waited in between drunkss
    '''A generic drinkable item, drink time is how long drinkAnim takes to play
    all subclasses must define a onDrunk method'''

    __slots__ = 'wait_in_state','drink_animation','animation_backup','state'
    def __init__(self, tag: str,drinkAnim:Animation.SimpleAnimation):
        super().__init__(tag)
        self.drink_animation = drinkAnim
        self.wait_in_state = drinkAnim.time_per_cycle
        self.animation_backup = self.animation
        self.state = self.NOT_DRINKING

    @final
    def startUse(self, inventory: UniversalInventory) -> None:
        self.state = self.DRINKING
        self.animation = self.drink_animation
    
    @final
    def duringUse(self, inventory: UniversalInventory) -> None:
        match self.state:
            case self.DRINKING:
                self.wait_in_state -= Time.deltaTime
                if self.wait_in_state <= Time.deltaTime:
                    for i,item in enumerate(inventory.inventory):
                        if item is self:
                            self.count -= 1
                            self.onDrunk(inventory)

                            if self.count == 0:
                                inventory.checkItem(i)
                            else:
                                self.wait_in_state = self.drink_animation.time_per_cycle
                                self.state = self.IN_BETWEEN_DRINKS
                                self.animation = self.animation_backup


            case self.IN_BETWEEN_DRINKS:
                self.wait_in_state -= Time.deltaTime
                if self.wait_in_state <= 0:
                    self.state = self.DRINKING
                    self.wait_in_state = self.drink_animation.time_per_cycle
                    self.animation = self.drink_animation
                    self.drink_animation.reset()

 
    @final
    def stopUse(self, inventory: UniversalInventory) -> None:
        self.animation = self.animation_backup
        self.wait_in_state = self.drink_animation.time_per_cycle
        self.drink_animation.reset()

    @abstractmethod
    def onDrunk(self,inventory:UniversalInventory): ...

class StrengthPotion(DrinkableItem):
    def __init__(self):
        drinkAnim = Animation.SimpleAnimation(Camera.CSurface(Textures.NULL,Vector2.zero(),(0,0)),2,Textures.items['drinkingstrengthpotion'])
        super().__init__(ITAG_STR_POTION, drinkAnim)
        self.animation.fps = 2

    def onDrunk(self,inventory:UniversalInventory):
        print('drunk!!! hehehehaw')
        SuperStrength1(inventory.entity)

class SpeedPotion(DrinkableItem):
    __slots__ = ()
    def __init__(self):
        drinkAnim = Animation.SimpleAnimation(Camera.CSurface(Textures.NULL,Vector2.zero(),(0,0)),2,Textures.items['drinkingspeedpotion'])
        super().__init__(ITAG_SPD_POTION, drinkAnim)
        self.animation.fps = 1


    def onDrunk(self,inventory:UniversalInventory):
        print('drunk!!! hehehehaw')
        Speed1(inventory.entity)
        Camera.set_camera_convergence_speed(6)

class BunnyEgg(Item): 
    entity_loaded = 'bunny'
    def __init__(self):
        super().__init__(ITAG_BUNNY_EGG)
        self.name = f"Bunny Spawn Egg"
        self.species =  'bunny'

class ItemArrow(Item):
    bow_shootable = True
    base_projectile = 'arrow'
    lore = 'chickeN!!!!'
    __slots__ = 'projectile'
    def __init__(self):
        super().__init__(ITAG_ARROW)
        self.projectile = self.base_projectile

class ItemArrowExplosive(Item):
    bow_shootable = True
    base_projectile = 'arrow'
    __slots__ = 'projectile'
    def __init__(self):
        super().__init__(ITAG_ARROW_EXPLOSIVE)
        self.projectile = self.base_projectile

class ItemArrowFunny(Item):
    bow_shootable = True
    base_projectile = 'funnyarrow'
    lore = 'get rekt'
    description = 'secretly OP'
    def __init__(self):
        super().__init__(ITAG_ARROW_FUNNY)
        self.projectile = self.base_projectile

class BowBase(Item):
    __slots__ = 'springyness','startTime','loadStage','max_pull_time','loaded_item','min_draw_time'
    def __init__(self,item_tag:str):
        super().__init__(item_tag)
        self.loadStage = 0.0
        self.startTime:float|None = None
        self.startTime = None
        self.springyness:float = 7.0 # used to calculate arrow speed
        self.min_draw_time = 0.5 # this is the minimum amount of time required so that the arrow in the inventory actually be consumbed
        self.max_pull_time = 5.0 #the maximum amount of time held down that should be counted towards the bow fire
        self.loaded_item:type["Entity"]|None = None
        
    
    def startUse(self,inventory: UniversalInventory):
        for i,item in enumerate(inventory.inventory):

            item:ItemArrow
            if item is not None and item.bow_shootable:
                self.startTime = Time.time
                return
        self.startTime = None

    def duringUse(self, inventory: UniversalInventory) -> None:
        if self.startTime is None or self.loaded_item is not None: return
        if Time.time - self.startTime < self.min_draw_time: return
        for i,item in enumerate(inventory.inventory):
            if item is not None and item.bow_shootable:
                item:ItemArrow
                self.loaded_item = Settings.SPAWNABLE_ENTITIES[item.projectile]
                item.count -= 1
                return inventory.checkItem(i)  # return None
    
    def stopUse(self,inventory:UniversalInventory) -> None:
        from .Components import Position
        if self.startTime is None or self.loaded_item is None: return
        assert isinstance(inventory,UniversalInventory)
        time = min(Time.time - self.startTime,self.max_pull_time)
        speed_modifier = self.getArrowSpeedFromTime(time)
        direction = (Camera.world_position(Input.m_pos) - inventory.entity.getComponent(Position.Position)).normalized
        direction.fromTuple(randomNudge(direction.x,direction.y,self.getArrowInstability(time)))
        inventory.entity.spawn_entity(self.loaded_item(inventory.entity.pos + direction/2,direction * speed_modifier,inventory.entity)) #type: ignore
        self.loaded_item = None
        self.startTime = None

    def getArrowSpeedFromTime(self,t:float) -> float: ...
        
    def getArrowInstability(self,t:float) -> float: ...

class Bow(BowBase):
    def __init__(self):
        super().__init__(ITAG_BOW)
    
    def getArrowSpeedFromTime(self,t:float) -> float:
        return tanh(t) * self.springyness

    def getArrowInstability(self,t:float) -> float: # this is how much the arrow should be randomized for 
        return 1/ ( 5.0 + (4.5 * (t - 0.3))**2)

class QuickBow(BowBase):
    def __init__(self):
        super().__init__(ITAG_SHORTBOW)
        self.springyness = 5.0
    
    def getArrowSpeedFromTime(self,t:float) -> float:
        return tanh(min(2*t,self.max_pull_time)) * self.springyness
    
    def getArrowInstability(self,t): # this is how much the arrow should be randomized for 
        return 1/ ( 5.0 + (3.5 * (t - 0.3))**2)+0.2

class DivineBow(BowBase):
    description = 'An ancient bow made of incredibly light yet springy material.'
    lore =  'DIS BOW IS SUPA OP'
    def __init__(self):
        super().__init__(ITAG_DIVINE_BOW)

        self.springyness = 10.0

    def getArrowSpeedFromTime(self, t: float) -> float:
        v = (t + 0.5)
        return tanh(v*v)  * self.springyness

    def getArrowInstability(self, t: float) -> float:
        return 0.0


