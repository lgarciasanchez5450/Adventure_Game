from Constants import *

from Inventory import InventoryInterface
from game_math import *
from Camera import CSurface
from pygame import Surface,font
from Animation import SimpleAnimation
class Item(UnInstantiable):
    csurface:CSurface
    animation:SimpleAnimation 
    count:int
    max_stack_count:int



class ItemSlot:
    UP = 0
    HOVER = 1
    PRESSED = 2
    font = font.SysFont("Arial",ITEM_COUNTER_SIZE)   
    def __init__(self,pos:tuple|list,index:int,inventory:InventoryInterface):
        self.index = index
        self.inventory = inventory
        self.pos = pos
        self.collider = Collider(pos[0],pos[1],ITEM_SIZE,ITEM_SIZE)
        self.surface = Surface(self.collider.size)
        self.bg_color = (50,70,60)
        self.state = 0
        self.hover_color = (70,90,90)

    def set_inventory(self,inventory:InventoryInterface):
        self.inventory = inventory

    def set_bgc(self,color:tuple):
        self.bg_color = color
        return self


    def update(self,m_pos_normalized:Vector2) -> Item|None:
        if self.collider.collide_point_inclusive(m_pos_normalized.tuple):
            self.state = ItemSlot.HOVER
            
        else:
            self.state = ItemSlot.UP

    def draw(self,surface:Surface):
        item:Item = self.inventory.seeIndex(self.index)
        if hasattr(item,'animation'):
            item.animation.animate()
        self.surface.fill(self.hover_color if self.state == self.HOVER else self.bg_color)
        if item is not None:
            self.surface.blit(item.animation.surf,(0,0))
            if item.count > 1:
                item_count = self.font.render(str(item.count),False,'white')

                self.surface.blit(item_count,(ITEM_SIZE-item_count.get_width(),ITEM_SIZE-item_count.get_height()))
                pass
        surface.blit(self.surface,self.pos)
