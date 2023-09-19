from Constants import * 
from Items import Item
_DEBUG_ = True

from game_math import Array


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
            inventory_item:Item
            if inventory_item is None and first_empty is None:
                first_empty = index
            elif item.canStack(inventory_item):
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

        if type(item) is type(i_item):
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

    def set_armour(self,armour:Item|None,body_space:str) -> object|None:
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
    
    def pop_selected(self) -> Item|None:
        return self.inventory.take(self.selected)
    

if __name__ == '__main__':
    inv1 = Inventory(10)
    

    print(inv1)