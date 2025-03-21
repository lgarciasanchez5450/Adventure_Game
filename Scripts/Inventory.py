import typing

from Utils.Array import Array
from Scripts.Item import Item

class Inventory:
    def __init__(self,spaces:int):
        self.inventory:Array[Item] = Array(spaces)
        self.slot_restrictions:dict[int,typing.Callable[[Item],bool]] = {} #will store slot indexes that have restrictions via a function that will accept the item and return True only if it fits

    def setItem(self,item: typing.Optional["Item"],index:int):
        '''
        The implementation should prioritize combining the items, if that doesn't work it will swap them
        Should return item that is left over or None if nothing is left over
        '''
        #check if new item passes slot restrictions
        if item is not None and index in self.slot_restrictions:
            
            if not self.slot_restrictions[index](item):  
                return item #test failed, return early
        i_item = self.inventory[index]
        if (item is not None and i_item is not None) and item.type is i_item.type:
            return self._addItem(item,index)
        else:
            # in all cases where the items arent compatible or if they are the but something went wrong
            return self.inventory.swap(index,item)

    def _addItem(self,item: "Item",index:int):
        '''Does not check if item & i_item are compatible, this should be done beforehand 
        returns item left over or none'''
        i_item = self.inventory[index]
        if i_item is None:
            return self.inventory.swap(index,item)
        if i_item.count == i_item.stack_size:
            return item
        to_transfer = i_item.stack_size - i_item.count # try to transfer as much as i_item can take
        if to_transfer > item.count: #if item does not have enough to transfer, limit to item's count
            to_transfer = item.count
        item.count -= to_transfer
        i_item.count += to_transfer
        return item if item.count else None
    
    def checkItem(self,index:int):
        '''
           *Run checks on item to make sure that it is valid
           *Runs slot restriction, Checks item count and removes it accordingly
           *Assumes that the index is not an empty slot '''
        item = self.inventory[index]
        if item is None: return
        if item.count <= 0:
            return self.inventory.remove(index)
        if index in self.slot_restrictions:
            if not self.slot_restrictions[index](item):
                return self.inventory.remove(index)

    def slotCompatible(self,item: "Item",index:int):
        return self.slot_restrictions.get(index,lambda x: True)(item)
  
    def fitItem(self,item :"Item"):
        empty_slots = []
        for index, i_item in enumerate(self.inventory):
            if i_item is None:
                empty_slots.append(index)
            elif i_item.type is item.type:
                if (i:= self._addItem(item,index)) is None:
                    return None
                item = i

        del index, i_item #type: ignore
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

    def seeIndex(self,index:int):
        return self.inventory[index]
    
    def addRestriction(self,index:int,func:typing.Callable[[Item],bool]):
        self.slot_restrictions[index] = func
        return self
    
    # def addArmourRestrictionsFromDictionary(self,dict:dict[int,tuple[str,...]]):
    #     '''Will add it to the end of the slots'''
    #     index = self.slot_restrictions.__len__() - dict.__len__()
    #     for i,string in enumerate(dict.values(),start = index):
    #         self.addRestriction(i,lambda item : item.armour_type == string)


class Hotbar:
    def __init__(self,inventory:Inventory,*spaces:int):
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
    
    def setItem(self,item:Item|None,index:int):
        '''
        The implementation should prioritize combining the items, if that doesn't work it will swap them
        Should return item that is left over or None if nothing is left over
        '''
        return self._inv.setItem(item,self._spaces[index])

    def seeIndex(self,index:int):
        return self._inv.inventory[self._spaces[index]]
    
    # def _addItemAsOne(self,item:"Item",index:int):
    #     self._inv._addItemAsOne(item,self._spaces[index])

    def fitItem(self,item:Item|None):
        empty_slots = []
        for index in self._spaces:
            inventory_item = self._inv.inventory[index]
            if inventory_item is None:
                empty_slots.append(index)
            elif item is not None and inventory_item.type is item.type:
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
        # self.item_selected.startUse(self._inv);  
        self.using_selected = True
        #if self.item_selected.count == 0:
        #    self._inv.inventory[self.selected] = None
        #    self.item_selected = None
        #    self.using_selected = False        

    def during_use_selected(self) -> None:
        #print(self.item_selected,self.using_selected)
        if self.item_selected is None or not self.using_selected: return
        # self.item_selected.duringUse(self._inv)
        if self.item_selected is None or self.item_selected.count == 0:
            self._inv.inventory[self.selected] = None
            self.using_selected = False

    def stop_use_selected(self):
        if self.item_selected is None: return
        # self.item_selected.stopUse(self._inv)
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

