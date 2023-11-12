import pygame
if __name__=='__main__':
    screen = pygame.display.set_mode((100,100),pygame.OPENGL)
    import Textures
    Textures.init()
from Constants import *
from Settings import BLOCK_SIZE,ITEM_SIZE, SLEEP_VELOCITY_THRESHOLD
import Textures
from Camera import NullCSurface
from game_math import cache,Vector2,Collider,get_most_sig_bits
from math import floor
from pygame.transform import smoothscale as image_scale
from game_random import generate_point_from
import Animation
from typing import Callable,TypeVar


_DEBUG_ = True
@cache
def get_surface(name):
    return image_scale(Textures.texture[name],(ITEM_SIZE,ITEM_SIZE))
class ArmourStats:
    wearable:bool = True

    __slots__ = ('type','defense')
    def __init__(self,type:str,defense:int) -> None:
        self.type = type
        self.defense = defense

    def hashcode(self):
        '''Should return 4 bytes as an int '''
        return (hash(self.type) ^ self.defense) & 0xFFFFFFFF


class DurabilityStats:
    breakable = True
    __slots__ = ('max_durability','durability')
    def __init__(self,max_durability:int,durability:int):
        self.max_durability = max_durability
        self.durability = durability

    def remove_durability(self,amount:int):
        self.durability -= amount
        if self.durability <= 0:
            self.durability = 0

    def hashcode(self):
        '''Should return 4 bytes as an int '''
        return ((self.max_durability + 53) * self.durability + 53 ) & 0xFFFFFFFF


nullFrame:pygame.Surface= Textures.texture['null.png']
class Item:

    def build(self):
        self.hashcode = 0  
        if self.armour_stats is not None:
            self.hashcode |= self.armour_stats.hashcode() << 32
        if self.durability_stats is not None:
            self.hashcode |= self.durability_stats.hashcode()
        
        self.hashcode <<= 16
        generic_code = ((get_most_sig_bits(self.damage,2)<<2)|(self.damage&0b11))
        generic_code <<=4
        generic_code |= ((get_most_sig_bits(self.max_stack_count,2)<<2)|(self.max_stack_count&0b11))
        generic_code <<=4
        generic_code |= ((get_most_sig_bits(self.mining_speed,2)<<2)|(self.mining_speed&0b11))
        self.hashcode |= generic_code

        return self

    __slots__ = ('name', 'max_stack_count', 'count', 'durability_stats', 'armour_stats', 'block', 'damage', 'mining_speed', 'fps', 'animation','frames','hashcode','left_click','right_click','left_hold','right_hold')
    def __init__(self,name:str,block:str|None=None):
        self.hashcode =None
        self.block = block# if this is not None then it needs to be a key <string> to the block that it should place  
        self.name = name
        self.max_stack_count = 1
        self.count = 1
        self.durability_stats:DurabilityStats|None = None
        self.armour_stats:ArmourStats|None = None
        self.damage = 0 
        self.mining_speed = 0 
        self.fps = 0 #this is for when the ItemWrapper <Entity> needs to create the animation. 
        self.frames:tuple[pygame.Surface]  = (Textures.texture.get(name+'.png',nullFrame),) # at most 60 frames 
        #self.path = f'{Textures.PATH()}Images\\items\\{name}'
        self.animation = Animation.SimpleAnimation(NullCSurface,self.fps,self.frames)
        self.left_click:Callable[[Item],None] = lambda t: None
        self.right_click:Callable[[Item],None] = lambda t : None
        self.left_hold:Callable[[Item],None] = lambda t: None
        self.right_hold:Callable[[Item],None] = lambda t: None

    def take_one(self):
        '''Splits an instance of a specific item (that has a count > 1) in two, one that it returns that has a count of 1 and it decrements the count of this item by 1'''
        if _DEBUG_ and self.count == 1: raise RuntimeError("Cannot split an item that has a count of one!")
        self.count -= 1
        return self.copy_one()
    
    def split_half(self):
        '''Splits an instance of a specific item (that has a count > 1) in two, one that it returns that has a count of ceil(self.count/2) and it decrements the count of this item by floor(count/2)'''
        if _DEBUG_ and self.count == 1: raise RuntimeError("Cannot split an item that has a count of one!")
        floored_half = self.count//2 
        self.count -= floored_half
        _new = self.copy_one()
        _new.count = floored_half
        return _new
    
    def leave_one(self):
        if _DEBUG_ and self.count == 1: raise RuntimeError("Cannot split an item that has a count of one!")
        _new = self.copy_one()
        _new.count = self.count-1
        self.count =1 
        return _new

    def copy_one(self):
        inst = Item(self.name,self.block)
        inst.durability_stats = self.durability_stats
        inst.armour_stats = self.armour_stats
        inst.max_stack_count = self.max_stack_count
        inst.fps = self.fps
        inst.damage = self.damage
        return inst
    
    def remove_one(self):
        self.count -= 1
        if self.count == 0:
            return True
        return False
        
    def setMaxCount(self,max_count):
        self.max_stack_count = max_count
        return self

    def setWearable(self,type,armour):
        self.armour_stats = ArmourStats(type,armour)
        return self
    
    def setBreakable(self,max,curr):
        self.durability_stats = DurabilityStats(max,curr)
        return self
    
    def setLeftClick(self,leftClick):
        self.left_click = leftClick
        return self

    @property
    def wearable(self) -> bool:
        return self.armour_stats is not None

   
    def canStack(self,other):
        '''Items can only stack with each other if they share the same name and hashcode method'''
        if other is None:
            return False
        assert isinstance(other,Item), 'Can only compare Items with other items'
        return self.name is other.name and self.hashcode == other.hashcode
    def __eq__(self,other) -> bool:
        return self is other        

    def __repr__(self):       
        return f"{self.name} <Item>: Count -> {self.count}"
import typing
ItemFactory = typing.Callable[[],Item]
ItemSystem:dict[str,ItemFactory] = {}
def registerItem(itemFactory:ItemFactory,name):
    registeringError = "Error in Registering Item: "+name
    global ItemSystem
    if name in ItemSystem:
        print("Cannot override a previous item registered in ItemSystem")
        raise RuntimeError()
    #Testing if item is good to add
    if not callable(itemFactory):
        print(registeringError)
        return
    testItem:Item = itemFactory()
    if testItem.hashcode is not None:
        print(registeringError)
        raise RuntimeError()
    if testItem.name is not name:
        print(registeringError)
        return
    print('Succesfully Registered item ->',name)
    ItemSystem[name] = itemFactory

def getItem(name:str) -> Item:
    if name not in ItemSystem:
        raise RuntimeError(f'Item of name {name} does not exist. Make sure it is registered!')
    return ItemSystem[name]().build()
    
def delItem(item:Item):
    import gc
    print("All references to item:",gc.get_referrers)

 
