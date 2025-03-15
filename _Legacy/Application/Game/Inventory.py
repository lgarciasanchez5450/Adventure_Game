from typing import Callable,Optional,Protocol,TYPE_CHECKING,Any
from .Constants import * 
from .Settings import STACK_COUNT_BY_TAG
from ..Utils.Math.game_math import Array

if TYPE_CHECKING: 
    from Application.Game.general_manager import AliveEntity
    from Application.Game.Items import *

class InventoryLike(Protocol):
    @property
    def spaces(self) -> int: ...
    def setItem(self,item:Optional["Item"],index:int) -> Optional["Item"]: ...
    def seeIndex(self,index:int) -> Optional["Item"]: ...
    def fitItem(self,item :Optional["Item"]) -> Optional["Item"]: ...

class UniversalInventory:
    def __init__(self,spaces:int,entity):
        self.spaces = spaces
        self.inventory:Array[Item] = Array.new(spaces)
        self.full = False
        self.entity:'AliveEntity' = entity
        self.selected:int = -1
        self.slot_restrictions:dict[int,Callable[[Item],bool]] = {} #will store slot indexes that have restrictions via a function that will accept the item and return True only if it fits

    def setItem(self,item: Optional["Item"],index:int):
        '''
        The implementation should prioritize combining the items, if that doesn't work it will swap them
        Should return item that is left over or None if nothing is left over
        '''
        #check if new item passes slot restrictions
        if index in self.slot_restrictions:
            if not self.slot_restrictions[index](item): #type: ignore
                #test failed, return early
                return item
            
        # the test is passed or there was no test
        if item is None: #we can just skip to swapping immediately
            return self.inventory.swap(index,item)
        
        if item.stackCompatible(self.inventory[index]): #if the objects can be combined
            # here i_item is guaranteed to not be None 
            i_item = self.inventory[index]
            if TYPE_CHECKING:
                assert isinstance(i_item,Item)

            if i_item.count == i_item.max_stack_count:
                return item
            to_transfer = min(i_item.max_stack_count - i_item.count,item.count) # we take the smaller value of how much the i_item needs to be full and how much item can give
            item.count -= to_transfer
            i_item.count += to_transfer
            if item.count == 0:
                return None
            else: 
                return item
        # in all cases where the items arent compatible or if they are the but something went wrong
        return self.inventory.swap(index,item)

    def _addItem(self,item: "Item",index:int):
        '''Does not check if item & i_item are compatible, this should be done beforehand 
        returns item left over or none'''

        i_item = self.inventory[index]
        if i_item is None:
            self.inventory[index] = item
            return None
    
        if i_item.count == i_item.max_stack_count:
            return item
        
        to_transfer = min(i_item.max_stack_count - i_item.count,item.count) # we take the smaller value of how much the i_item needs to be full and how much item can give
        item.count -= to_transfer
        i_item.count += to_transfer
        if item.count == 0:
            return None
        else: 
            return item
        
    def _addItemAsOne(self,item: "Item", index:int):
        '''Does not check if item & i_item are compatible, this should be done beforehand 
        returns item left over or none. On top of that, assumes that item.count == 1'''
        i_item = self.inventory[index]
        if i_item is None:
            self.inventory[index] = item
            return None

        if i_item.count == i_item.max_stack_count:
            return item
        else:
            i_item.count += 1
        return None
    
    def checkItem(self,index:int):
        '''
           *Run checks on item to make sure that it is valid
           *Runs slot restriction, Checks item count and removes it accordingly
           *Assumes that the index is not an empty slot '''
        item = self.inventory[index]
        if TYPE_CHECKING: assert isinstance(item,Item)
        if item.count <= 0:
            return self.inventory.remove(index)
        if index in self.slot_restrictions:
            if not self.slot_restrictions[index](item):
                return self.inventory.remove(index)
   
    def getItem(self,index: int):
        '''Returns the original reference to the item inside the inventory, relinquishing its own reference to it'''
        return self.inventory.take(index)

    def slotCompatible(self,item: "Item",index:int):
        return self.slot_restrictions.get(index,lambda x: True)(item)
  
    def fitItem(self,item :Optional["Item"]):
        empty_slots = []
        for index, inventory_item in enumerate(self.inventory):
            inventory_item:Item
            if inventory_item is None:
                empty_slots.append(index)
            elif inventory_item.stackCompatible(item):
                assert not isinstance(item, type(None)) #for typechecking purposes only! 
                item = self._addItem(item,index)
                if item is None:
                    return None

        del index, inventory_item #type: ignore
        #if it has reached here then there is no previously existing item of the same type but there are empty slots
        for slot in empty_slots:
            if slot in self.slot_restrictions:
                if self.slot_restrictions[slot](item): #type: ignore
                    self.inventory[slot] = item
                    return None
            else:
                self.inventory[slot] = item
                return 
        return item
    '''
    def get_selected(self) -> None:
        return self.inventory[self.selected]
    
    def start_use_selected(self) -> None:
        item:Item = self.inventory[self.selected]
        if item is None: return
        item.startUse(self);  
        if item.count == 0:
            self.inventory[self.selected] = None

    def stop_use_selected(self):
        item:Item = self.inventory[self.selected]
        if item is None: return
        item.stopUse(self)
        if item.count == 0:
            self.inventory[self.selected] = None
    
    def setSelected(self,newSelected:int) -> None:
        self.stop_use_selected()
        self.selected = newSelected
    
    def pop_selected(self) -> None:
        return self.inventory.take(self.selected)          
    '''
    def seeIndex(self,index:int):
        return self.inventory[index]

    @property
    def added_spd(self) -> float:
        return 0

    @property
    def added_def(self) -> int:
        return 0
    
    def addRestriction(self,index:int,func:Callable[[Any],bool]):
        self.slot_restrictions[index] = func
        return self
    
    def addArmourRestrictionsFromDictionary(self,dict:dict[int,tuple[str,...]]):
        '''Will add it to the end of the slots'''
        index = self.slot_restrictions.__len__() - dict.__len__()
        for i,string in enumerate(dict.values(),start = index):
            self.addRestriction(i,lambda item : item.armour_type == string)
    def swapIndex(self,index1:int,index2:int) -> None:
        self.inventory.swapIndices(index1,index2)


class Hotbar:
    def __init__(self,inventory:UniversalInventory,*spaces:int):
        '''Spaces should be indexes  '''
        self._inv = inventory
        self.len = len(spaces)
        self._spaces = spaces # offers a level of indirection to map hotbar indexes to inventory indexs
        self.selected:int =  0 # this is a hotbar index
        self.using_selected:bool = False
        # helper variables for item use

    @property
    def spaces(self):
        return self.len

    def __len__(self) -> int:
        return self.len
    
    def setItem(self,item:Optional["Item"],index:int):
        '''
        The implementation should prioritize combining the items, if that doesn't work it will swap them
        Should return item that is left over or None if nothing is left over
        '''
        return self._inv.setItem(item,self._spaces[index])

    def seeIndex(self,index:int):
        return self._inv.inventory[self._spaces[index]]
    
    def _addItemAsOne(self,item:"Item",index:int):
        self._inv._addItemAsOne(item,self._spaces[index])

    def fitItem(self,item:Optional["Item"]):
        empty_slots = []
        for index in self._spaces:
            inventory_item = self._inv.inventory[index]
            if inventory_item is None:
                empty_slots.append(index)
            elif inventory_item.stackCompatible(item):
                assert not isinstance(item, type(None))
                item = self._inv._addItem(item,index)
                if item is None:
                    return None

        del index, inventory_item #type: ignore
        #if it has reached here then there is no previously existing item of the same type but there are empty slots
        for slot in empty_slots:
            if slot in self._inv.slot_restrictions:
                if self._inv.slot_restrictions[slot](item): #type: ignore
                    self._inv.inventory[slot] = item
                    return None
            else:
                self._inv.inventory[slot] = item
                return 
        return item
    
    @property
    def item_selected(self):
        return self._inv.inventory[self._spaces[self.selected]]

    def seeSelected(self):
        return self.seeIndex(self.selected)
    
    def start_use_selected(self) -> None:
        if self.item_selected is None: return
        self.item_selected.startUse(self._inv);  
        self.using_selected = True
        #if self.item_selected.count == 0:
        #    self._inv.inventory[self.selected] = None
        #    self.item_selected = None
        #    self.using_selected = False        

    def during_use_selected(self) -> None:
        #print(self.item_selected,self.using_selected)
        if self.item_selected is None or not self.using_selected: return
        self.item_selected.duringUse(self._inv)
        if self.item_selected is None or self.item_selected.count == 0:
            self._inv.inventory[self.selected] = None
            self.using_selected = False

    def stop_use_selected(self):
        if self.item_selected is None: return
        self.item_selected.stopUse(self._inv)
        self.using_selected = False
        if self.item_selected is None or self.item_selected.count == 0:
            self._inv.inventory[self.selected] = None
    
    def setSelected(self,newSelected:int) -> None:
        if self.using_selected:
            self.stop_use_selected()
        self.selected = newSelected
        if self.using_selected:
            self.start_use_selected()

    def getSelected(self):
        '''Will return the original item while removing it from the hotbar.\n
        If only using for information then use seeSelected()'''
        return self._inv.inventory.take(self._spaces[self.selected])          


class ArmorInventory:
    def __init__(self,*spaces:str):
        self.spaces = len(spaces)
        self.inventory = {}
        for space in spaces:
            self.inventory[space] = None
    def seeIndex(self,index:str):
        return self.inventory[index]

    def set_armour(self,armour:Optional['Item'],body_space:str) ->Optional['Item']:
        '''
        Should return the armour that is left in the hand of the player when tried to put on
        First argument is the Armour <Item> that needs to be equipped, and the next is where 
        it is being attempted to be put
        '''
        if armour is None:
            prev,self.inventory[body_space] = self.inventory[body_space],armour
            return prev

        if armour.armour_stats is None: return armour
        if armour.armour_stats.type is not body_space: return armour
        if body_space in self.inventory.keys():
            prev,self.inventory[body_space] = self.inventory[body_space], armour
            return prev
        return armour

    @property
    def added_def(self):
        return 0

    @property
    def added_atk(self):
        return 0
     
    @property
    def added_dmg(self):
        return 0
    
    @property
    def added_spd(self):
        return 0
    
    @property
    def added_maxhp(self):
        return 0

