from Constants import * 
from Settings import STACK_COUNT_BY_TAG
from typing import Callable
_DEBUG_ = True

from game_math import Array,UnInstantiable
class ArmourStats:
    type:str
class Item(UnInstantiable):
    count:int
    tag:str
    armour_stats:ArmourStats
    durability_stats:object
    @property
    def max_stack_count(self) -> int:...
    def canStack(self,other) -> bool: ...
    def split(self): ...
    def startUse(self,inventory:object): ...
    def stackCompatible(self,other) -> bool: ...
    def stopUse(self,inventory:object): ...
    
class InventoryInterface(UnInstantiable):
    def seeIndex(self,index:int) -> Item: ...


class Inventory:
    def __init__(self,spaces:int):
        self.spaces = spaces
        self.inventory:Array[Item] = Array.new(spaces)
        self.full = False
        self._any_empty = True

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
    
    def any_empty(self) -> bool:
        if self._any_empty is not None: return self._any_empty
        for item in self.inventory:
            if item is None:
                self._any_empty = True
                return True
        self._any_empty = False
        return False
        #could be rewritten as any([item is None for item in self.inventory])

    
    def add_item(self,item:Item) -> bool:
        '''Returns True if the item that was checked is FULLY picked up, and is safe to remove from the camera'''
        self._any_empty = None
        first_empty = None
        for index, inventory_item in enumerate(self.inventory):
            if inventory_item is None and first_empty is None:
                first_empty = index
            elif item.canStack(inventory_item):
                inventory_item:Item
                if inventory_item.count + item.count <= inventory_item.max_stack_count:
                    inventory_item.count += item.count
                    item.count = 0
                    return True
                elif inventory_item.count < inventory_item.max_stack_count:
                    #it is guaranteed that item.count will be above 0
                    to_take = min(inventory_item.max_stack_count-inventory_item.count,item.count)
                    inventory_item.count += to_take
                    item.count -= to_take
                    return False

        if first_empty is not None:
            #if it has reached here then there is no previously existing item of the same type but there is an empty slot   
            self.inventory[first_empty] = item
            return True
        return False
    

    def set_item(self,item:Item|None,index:int) -> Item|None:
        if _DEBUG_ and not isinstance(index,int): raise TypeError('Incorrect argument type')
        return self.inventory.swap(index,item)

    def place_item(self,item:Item|None,index:int) -> Item|None:
        '''This is essentially what happens when you left click
        if the types are the same then the item should try to add itself to the slot, else then it should just call set_item
        Return value is the item that should be what is left in the players hand after clicking'''

        i_item:Item = self.inventory[index]
        if item is None:
            return self.inventory.take(index)

        if  item.canStack(i_item):
            if i_item.count + item.count <= i_item.max_stack_count:
                i_item.count += item.count
                i_item.count = 0

                return None
            elif i_item.count < i_item.max_stack_count:
                to_take = min(i_item.max_stack_count-i_item.count,item.count)
                i_item.count += to_take
                item.count -= to_take
                #it is guaranteed that item.count will be above 0 (if my maths are correct)
                return item
            
        else:
            return self.set_item(item,index)

    def take_one(self,slot:int):
        self._any_empty = None #next time any_empty method is called it must recalculate it.
        #first if there is a count of one then just take the rest, else if more than one take one
        item = self.inventory[slot]
        if item is None: return None
        if item.count == 1:
            return self.take_stack(slot)
        else:
            return item.split()

    def take_stack(self,slot) -> object|None:
        self._any_empty = None #next time any_empty method is called it must recalculate it.
        #first check if there is anything in that slot
        return self.inventory.take(slot)
    
    def __str__(self):
        return f"{[str(item) for item in self.inventory]}, len: {self.spaces if self.spaces == len(self.inventory) else 'Error'}"



class ArmorInventory:
    def __init__(self,*spaces:str):
        self.spaces = len(spaces)
        self.inventory = {}
        for space in spaces:
            self.inventory[space] = None
    def seeIndex(self,index:str):
        return self.inventory[index]

    def set_armour(self,armour:Item|None,body_space:str) -> Item|None:
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

class HotbarInventory(Inventory):
    def __init__(self,spaces):
        super().__init__(spaces)
        self.selected:int = 0 #should be a number from [0,spaces-1]

    def get_selected(self) -> Item|None:
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


    
    def pop_selected(self) -> Item|None:
        return self.inventory.take(self.selected)
    
class InventoryUnion:
    def __init__(self,*inventories:Inventory) -> None:

        self.inventories = inventories
        self.inventories = {
            #0:inv1,
            #10:inv2,
            #30:inv3
        }
        self._index = 0
        for inv in inventories:
            self.inventories[self._index] = inv
            self._index += inv.spaces
    
    def addInventory(self,inventory:Inventory):
        if inventory.spaces < 1: raise ValueError("Inventory must have at least one space")
        self.inventories[self._index] = inventory
        self._index += inventory.spaces

    def setItem(self,index):...

class UniversalInventory:
    def __init__(self,spaces:int,entity:object):
        self.spaces = spaces
        self.inventory:Array[Item] = Array.new(spaces)
        self.full = False
        self.entity = entity
        self.selected:int = -1
        self.slot_restrictions:dict[int,Callable[[Item],bool]] = {} #will store slot indexes that have restrictions via a function that will accept the item and return True only if it fits


    def setItem(self,item:Item|None,index:int):
        '''
        The implementation should prioritize combining the items, if that doesn't work it will swap them
        Should return item that is left over
        '''
        #check if new item passes slot restrictions
        if index in self.slot_restrictions:
            if not self.slot_restrictions[index](item):
                #test failed, return early
                return item
        # the test is passed
        if item is None: #we can just skip to swapping immediately
            return self.inventory.swap(index,item)
        
        if item.stackCompatible(self.inventory[index]): #if the objects can be combined
            # here i_item is guaranteed to not be None 
            i_item = self.inventory[index]
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

    def _addItem(self,item:Item,index:int) -> Item|None:
        '''Does not check if item & i_item are compatible, this should be done beforehand 
        returns item left over or none'''
        i_item = self.inventory[index]
        if i_item.count == i_item.max_stack_count:
            return item
        
        to_transfer = min(i_item.max_stack_count - i_item.count,item.count) # we take the smaller value of how much the i_item needs to be full and how much item can give
        item.count -= to_transfer
        i_item.count += to_transfer
        if item.count == 0:
            return None
        else: 
            return item

    def checkItem(self,index):
        '''
           *Run checks on item to make sure that it is valid
           *Runs slot restriction, Checks item count and removes it accordingly'''
        if self.inventory[index].count <= 0:
            return self.inventory.remove(index)
        if index in self.slot_restrictions:
            if not self.slot_restrictions[index](self.inventory[index]):
                return self.inventory.remove(index)

    def fitItem(self,item:Item) -> Item|None:
        empty_slots = []
        for index, inventory_item in enumerate(self.inventory):
            if inventory_item is None:
                empty_slots.append(index)
            elif item.stackCompatible(inventory_item):
                item = self._addItem(item,index)
                if item is None:
                    return None
        del index, inventory_item
        #if it has reached here then there is no previously existing item of the same type but there are empty slots
        for slot in empty_slots:
            if slot in self.slot_restrictions:
                if self.slot_restrictions[slot](item):
                    self.inventory[slot] = item
                    return None
        return None

    def get_selected(self) -> Item|None:
        return self.inventory[self.selected]
    
    def start_use_selected(self) -> None:
        item:Item = self.inventory[self.selected]
        if item is None: return
        item.startUse();  
        if item.count == 0:
            self.inventory[self.selected] = None

    def stop_use_selected(self):
        item:Item = self.inventory[self.selected]
        if item is None: return
        item.stopUse()
        if item.count == 0:
            self.inventory[self.selected] = None
    
    def setSelected(self,newSelected:int) -> None:
        self.stop_use_selected()
        self.selected = newSelected
    
    def pop_selected(self) -> Item|None:
        return self.inventory.take(self.selected)     
        
if __name__ == '__main__':
    inv1 = Inventory(10)
    

    print(inv1)