from ..Fonts import item_counter_font
from ...GuiFramework.Input import Input
from .Constants.Items import ITEM_SIZE
from .. import Textures
from ..Utils.TextRenderer import TextRenderer
from ..Fonts import item_title_font,item_counter_font,item_description_font,item_lore_font
from ...GuiFramework import *
from ..Game.Inventory import InventoryLike
from ..Game.general_manager import AliveEntity, Hotbar
from ..Game.Items import Item

ITEM_SPACING = 4

#### UI ####
class InventoryUI(DrawBase):
    order_in_layer = 3
    # __slots__ = 'screen_center','inventory','armour_inventory','inventory_size','has_hotbar','inventory_dont_do','slots_width','entity','slot_spacing','slots_center',\
    # 'armour_slots_center','hb_slots_center','in_hand','items_offset','slots','armour_offset','armour_slots','hotbar','hb_size','hotbar','hb_offset','hb_slots'
    def __init__(self,topleft:tuple[int,int],items_size:tuple[int,int],item_descriptor:"ItemDescriptor",hand:ObjectValue):
        self.rect = Rect(topleft, (items_size[0]*(ITEM_SIZE+8+ITEM_SPACING)-ITEM_SPACING,items_size[1]*(ITEM_SIZE+8+ITEM_SPACING)-ITEM_SPACING))
        self.items_size = items_size
        self.surface = Surface((0,0))
        self.hand = hand
        self.inventory:None|InventoryLike = None
        self.item_descriptor = item_descriptor
        self.slots_width = 9
        self.entity:None|AliveEntity = None
        self.phover = False
        
        self.hover_index = -1

    def setInventory(self,inventory:InventoryLike,hotbar_reserved:tuple[int,...] = tuple()):
        self.inventory = inventory
        self.slot_rects:list[Rect] = []
        self.slot_pointers:list[int] = []
        for i in range(inventory.spaces):
            # two ways to stop hotbar slots to be shown twice
            # way 1 is to simply skip over them when creating the ItemSlots
            # this could lead to empty spaces if there hotbar slots in the middle of the main inventory
            # way 2 is to only increment <i> if the current index is not currently part of the hotbar so basically it will make the Itemslots appear continuous 
            
            # for now imma just skip them and still increment <i> to clearly show if im skpping any so any bugs will be found easily
            if i in hotbar_reserved: continue #there.. happy??
            x = (i % self.items_size[0]) * (ITEM_SIZE + ITEM_SPACING + 8)
            y = (i // self.items_size[0]) * (ITEM_SIZE + ITEM_SPACING + 8)
            self.slot_rects.append(Rect(x,y,ITEM_SIZE+8,ITEM_SIZE+8))
            self.slot_pointers.append(i)
        # if self.has_hotbar:
        #     self.hb_offset = self.screen_center+self.hb_slots_center - Vector2(self.hb_size * self.slot_spacing,self.slot_spacing)/2 
        #     self.hb_slots = [ItemSlot((i*self.slot_spacing+self.hb_offset[0],self.slot_spacing+self.hb_offset[1]),i,self.hotbar) for i in range(self.hb_size)] #type: ignore

        # armour_size = Vector2(self.slot_spacing,self.slot_spacing * self.armour_inventory.spaces)
        # self.armour_offset = self.screen_center + self.armour_slots_center - armour_size/2
        # self.armour_slots = [ItemSlot((self.armour_offset[0],i*self.slot_spacing+self.armour_offset[1]),name,self.armour_inventory) for i,name in enumerate(self.armour_inventory.inventory)]#type: ignore
        # for armour_slot in self.armour_slots:
        #     armour_slot.bg_color = (60,30,25)

    def update(self,input:Input):
        # curr_hover = None
        # curr_position:tuple = (0,0)
        if not self.inventory: return
        hover = self.rect.collidepoint(input.mpos)
        if hover: 
            # if input.
            #     self.putted_inv:set[int] = set()
            #     self.putted_hotbar:set[int] = set()
            # self.relative_mouse_position_normalized = (Input.m_pos_normalized) @ (self.thingy)
            # self.rel_mouse_pos = (self.relative_mouse_position_normalized+ones) @ (self.surface_size/2)
            # self.rel_mouse_pos_int = Vector2Int.newFromTuple(self.rel_mouse_pos.tuple_ints)
            input.mousex -= self.rect.left
            input.mousey -= self.rect.top
            for r,i in zip(self.slot_rects,self.slot_pointers):
             
                if r.collidepoint(input.mpos):
                    if input.mb1d:
                        self.hand.set(self.inventory.setItem(self.hand.get(),i))
                    item = self.inventory.seeIndex(i)
                    if self.item_descriptor.item is not item:
                        self.item_descriptor.setItem(item,(r.right+self.rect.left,r.top+ self.rect.top))
                    self.hover_index = i
                    break

            else:
                self.hover_index = -1
                if self.item_descriptor.item is not None:
                    self.item_descriptor.setItem(None)

            input.mousex += self.rect.left
            input.mousey += self.rect.top
      
            # if current_inventory_hover_index != -1 and self.inventory is not None:
            #     if '1' in Input.KDQueue: #and current_inventory_hover_index != self.hotbar.spaces[0]:
            #         self.inventory.swapIndex(current_inventory_hover_index,self.hotbar.spaces[0])
            #         #self.inventory.inventory[current_inventory_hover_index] = self.hotbar.setItem(self.inventory.getItem(current_inventory_hover_index),0)
            #     if '2' in Input.KDQueue:
            #         self.inventory.swapIndex(current_inventory_hover_index,self.hotbar.spaces[1])
            #     if '3' in Input.KDQueue:
            #         self.inventory.swapIndex(current_inventory_hover_index,self.hotbar.spaces[2])
            #     if '4' in Input.KDQueue:
            #         self.inventory.swapIndex(current_inventory_hover_index,self.hotbar.spaces[3])
            #     if '5' in Input.KDQueue:
            #         self.inventory.swapIndex(current_inventory_hover_index,self.hotbar.spaces[4])
            #     if '6' in Input.KDQueue:
            #         self.inventory.swapIndex(current_inventory_hover_index,self.hotbar.spaces[5])
            #     if '7' in Input.KDQueue:
            #         self.inventory.swapIndex(current_inventory_hover_index,self.hotbar.spaces[6])
            #     if '8' in Input.KDQueue:
            #         self.inventory.swapIndex(current_inventory_hover_index,self.hotbar.spaces[7])
            #     if '9' in Input.KDQueue:
            #         self.inventory.swapIndex(current_inventory_hover_index,self.hotbar.spaces[8])
            # for slot in self.armour_slots:
            #     slot.update(self.rel_mouse_pos)
            #     if slot.state == slot.HOVER:
            #         curr_position = slot.pos #type: ignore
            #         curr_hover = self.armour_inventory.seeIndex(slot.index) #type: ignore
            #         if Input.m_u1:
            #             self.in_hand = self.armour_inventory.set_armour(self.in_hand,slot.index) #type: ignore
        elif self.phover:
            self.hover_index = -1
            self.item_descriptor.setItem(None)
        self.phover = hover
    
       
       
        # else:
        #     if Input.m_d1 and self.in_hand is not None:
        #         spawn_item(self.in_hand,self.entity.pos.copy(),Input.m_pos_normalized*2)
        #         self.in_hand = None
        # if self.hover_item is not curr_hover:
        #     self.hover_item_pos = curr_position #type: ignore
        #     self.hover_item = curr_hover
        #     itemDescriptor.setItem(curr_hover)

    def onResize(self,size:tuple[int,int]):
        self.surface = Surface(self.rect.size)
        self.surface.set_colorkey((0,0,0))


    def draw(self,surf:Surface):
        assert self.inventory

        for r,i in zip(self.slot_rects,self.slot_pointers):
            if self.hover_index == i:
                draw.rect(self.surface,(120,119,120),r)
            else:
                draw.rect(self.surface,(140,139,140),r)
            item = self.inventory.seeIndex(i)
            if item:
                self.surface.blit(item.animation.surf,r.move(4,4))
           
        # if self.in_hand is not None:
        #     in_hand_pos = (self.rel_mouse_pos.x-ITEM_SIZE//2,self.rel_mouse_pos.y-ITEM_SIZE//2)
        #     self.surface.blit(self.in_hand.animation.surf,in_hand_pos)
        #     if self.in_hand.count > 1:
        #         item_count = item_counter_font.render(str(self.in_hand.count),False,'white')
        #         self.surface.blit(item_count,(in_hand_pos[0] + ITEM_SIZE-item_count.get_width(),in_hand_pos[1] + ITEM_SIZE-item_count.get_height()))

        # entity = self.entity.csurface.surf,2) # TODO: Optimize
        # draw.rect(self.surface,(70,70,70),entity.get_rect().move(self.screen_center.x-100,10))
        # self.surface.blit(entity,(self.screen_center.x-100,10))
        surf.blit(self.surface,self.rect)

        # if (self.hover_item is not None):
        #     if Settings.ITEM_DESCRIPTION_USES_MOUSE:
        #         mouse_offset = Vector2Int(7,-4)
        #         itemDescriptor.draw(Camera.Window.window.world_surface,Vector2Int(self.pixel_topleft[0],self.pixel_topleft[1]) + mouse_offset + self.rel_mouse_pos_int)
        #     else: 
        #         itemDescriptor.draw(Camera.Window.window.world_surface,Vector2Int(self.pixel_topleft[0]+self.hover_item_pos[0]+ITEM_SIZE,self.pixel_topleft[1]+self.hover_item_pos[1]+ITEM_SIZE//2))

    # def close(self):
    #     showingUIs.set(Null)
    #     if self.in_hand is not None:
    #         spawn_item(self.in_hand,self.entity.pos.copy(),Input.m_pos_normalized*2)
    #         self.in_hand = None

class HotBarUI(DrawBase):
    order_in_layer = 1
    def __init__(self):
        selectedFrame = Textures.user_interface['hotbar']['selection_frame'] #type: ignore
        assert isinstance(selectedFrame, Surface)
        self.selectedFrame = selectedFrame
        self.slot_spacing = 4 #this is how many pixels will be between the edges of each
        self.background_color = (120,120,120,160)    #RGBA
        self.bg_surface = Surface((0 * (self.slot_spacing + ITEM_SIZE) + self.slot_spacing, ITEM_SIZE + self.slot_spacing * 2),const.SRCALPHA)
        self.rect = self.bg_surface.get_rect()
        self.on_rect_change_event:Event[[]] = Event()
        self.slot_rects = []
        self.hotbar = None

    def setHotbar(self,hotbar:Hotbar):
        self.hotbar = hotbar

        self.slot_rects = [Rect(i*(ITEM_SIZE+self.slot_spacing)+self.slot_spacing,self.slot_spacing,ITEM_SIZE+self.slot_spacing,ITEM_SIZE+self.slot_spacing) for i in range(self.hotbar.len)] #type: ignore
        self.rect.width = hotbar.len * (self.slot_spacing + ITEM_SIZE) + self.slot_spacing
        self.rect.height = self.slot_spacing * 2 + ITEM_SIZE
        self.bg_surface = Surface(self.rect.size,const.SRCALPHA)
        self.bg_surface.fill(self.background_color)
        self.on_rect_change_event.fire()

    def onResize(self,size:tuple[int,int]):
        self.bg_surface = Surface(self.rect.size,const.SRCALPHA)
        if self.hotbar:
            self.bg_surface.fill(self.background_color)
            #self.bg_surface.blit(self.selectedFrame,(self.hotbar.selected * (ITEM_SIZE + self.slot_spacing) ,0))   

    def setSelected(self,hotbar_index:int):
        if self.hotbar is None: return

        self.hotbar.setSelected(hotbar_index)
        self.bg_surface.fill(self.background_color)
        #self.bg_surface.blit(self.selectedFrame,(self.hotbar.selected * (ITEM_SIZE + self.slot_spacing) ,0))   

    def update(self,input:Input):
        if self.hotbar is None: return
        def consumeInput(key:str):
            if key in input.KDQueue:
                input.KDQueue.remove(key)
                return True
            return False

        for i, key in enumerate(['1','2','3','4','5','6','7','8','9']):
            if consumeInput(key):
                self.setSelected(i)
                break
            
        if input.wheel:
            self.hotbar.setSelected((self.hotbar.selected + input.wheel) % self.hotbar.len)
            self.bg_surface.fill(self.background_color)
            #self.bg_surface.blit(self.selectedFrame,(self.hotbar.selected * (ITEM_SIZE + self.slot_spacing) ,0))
        if self.rect.collidepoint(input.mpos) and input.mb1d:
            input.mousex -= self.rect.left
            input.mousey -= self.rect.top
            for i,r in enumerate(self.slot_rects):
                if r.collidepoint(input.mpos):
                    self.hotbar.setSelected(i)
                    self.bg_surface.fill(self.background_color)
                    #self.bg_surface.blit(self.selectedFrame,(self.hotbar.selected * (ITEM_SIZE + self.slot_spacing) ,0))
            input.mb1d = False
            input.mousex -= self.rect.left
            input.mousey -= self.rect.top

    def draw(self,surf:Surface):
        if self.hotbar is None: return

        surf.blit(self.bg_surface,self.rect)
        surf.blit(self.selectedFrame,(self.rect.move(self.hotbar.selected * (ITEM_SIZE + self.slot_spacing) ,0)))   
        for i,r in enumerate(self.slot_rects):
            if (item := self.hotbar.seeIndex(i)) is not None:
                item.animation.animate()
                surf.blit(item.animation.surf,
                          (r.left+self.rect.left,r.top+self.rect.top)
                )

class ItemObjectRenderer(DrawBase):
    order_in_layer = 5
    def __init__(self,shared_object:ObjectValue) -> None:
        self.shared_object:ObjectValue["Item"] = shared_object
        self.rect = Rect(0,0,ITEM_SIZE,ITEM_SIZE)

    def update(self,input:Input):
        self.rect.center = input.mpos

    def draw(self,surf:Surface):
        if self.shared_object.obj is not None:
            surf.blit(self.shared_object.obj.animation.csurface.surf,self.rect)

class ItemDescriptor(DrawBase):
    order_in_layer = 5
    def __init__(self):
        self.title_renderer = TextRenderer(item_title_font,(255,255,255))
        self.description_renderer = TextRenderer(item_description_font,(255,255,255))
        self.lore_renderer = TextRenderer(item_lore_font,(255,255,255))
        self.rect = Rect(0,0,1,1)
        self.item:Item|None = None
        self.item_name:Surface = Surface((0,0))
        self.item_lore:Surface = Surface((0,0))
        self.item_desc:Surface = Surface((0,0))
        self.bg_surf = Surface(self.rect.size)
        self.bg_surf.set_colorkey((0,0,1))
        self.bg_surf.set_alpha(200)
        
    def setItem(self,item:Item|None,pos:tuple[int,int]|None = None):
        self.item = item
        if item is not None:
            self.item_name = self.title_renderer.render_align(item.name)
            self.item_lore = self.title_renderer.render_align(item.lore)
            self.item_desc = self.title_renderer.render_align(item.description)
            
            self.rect.width = max(self.item_name.get_width(),self.item_desc.get_width(),self.item_lore.get_width())     
            self.rect.height = self.item_name.get_height() +  self.item_desc.get_height() + self.item_lore.get_height()
            # print(self.item_name.get_width(),self.item_desc.get_width(),self.item_lore.get_width())
            self.bg_surf = Surface(self.rect.size)
            self.bg_surf.set_colorkey((0,0,1))
            self.bg_surf.set_alpha(200)
        if pos is not None:
            self.rect.topleft = pos

    def update(self,input:Input):
        if self.item is None: return


    def draw(self,surf:Surface):
        if self.item is None: return
        surf.blit(self.bg_surf,self.rect)
        surf.blit(self.item_name,self.rect.topleft)
        surf.blit(self.item_lore,(self.rect.left,self.rect.top+self.item_name.get_height()))
        surf.blit(self.item_desc,(self.rect.left,self.rect.bottom-self.item_desc.get_height()))



class HealthBar(DrawBase):
    PRIMARY_COLOR = (255,255,255)
    OUTLINE_COLOR = (255,255,255)
    OUTLINE_WIDTH = 1
    BAR_WIDTH = 6 # in pixels
    BAR_HEIGHT = 20 # in pixels
    BAR_SPACING = 3
    def __init__(self,pos:tuple[int,int],percents:tuple[float,...] = (0.05,0.10,0.40,0.60,0.75)):
        assert percents == tuple(sorted(percents)), f'percents must be sorted {percents} vs {tuple(sorted(percents))}'
        self.entity:AliveEntity|None = None
        
        self.bars = len(percents)
        self.percents = percents

        width = self.BAR_SPACING + (self.BAR_WIDTH + self.BAR_SPACING) * self.bars
        height = self.BAR_HEIGHT + 2 * (self.BAR_SPACING)
        self.rect = Rect(pos[0],pos[1],width,height)
        self.current_bars = 0

    def calculate_bars(self) -> int:
        if self.entity is None: return 0 
        percent_health = self.entity.health / self.entity.total_health
        for i,percent in enumerate(self.percents):
            if percent_health < percent:
                return i
        return self.bars
    
    def setEntity(self,entity:AliveEntity):
        self.entity= entity
            

    # def _draw_surface(self):
    #     self.csurf.surf.fill(NULL_COLOR)
    #     #draw the outlines
    #     for i in range(self.OUTLINE_WIDTH): # we draw smaller 1 pixel outlines until we get the desired width
    #         pygame.draw.lines(self.csurf.surf,self.OUTLINE_COLOR,True,([i,i],[self.csurf.surf.get_width()-i-1,i],[self.csurf.surf.get_width()-i-1,self.csurf.surf.get_height()-1-i],[i,self.csurf.surf.get_height()-i-1]))

    #     top = self.OUTLINE_WIDTH + self.BAR_SPACING
    #     width = self.OUTLINE_WIDTH + self.BAR_SPACING
    #     for _ in range(self.current_bars):
    #         pygame.draw.rect(self.csurf.surf,self.PRIMARY_COLOR,(width,top,self.BAR_WIDTH,self.BAR_HEIGHT))
    #         width += self.BAR_WIDTH + self.BAR_SPACING

    def update(self,input:Input):
        if self.entity is None: return
        new_bars = self.calculate_bars()
        if self.current_bars != new_bars:
            self.current_bars = new_bars
        if self.entity.dead:
            self.entity = None
    
    def draw(self,surf:Surface):
        draw.rect(surf,(10,10,10),self.rect,0,2)
        for i in range(self.current_bars):
            draw.rect(surf,(50,190,50),
                      (self.rect.left + self.BAR_SPACING + (self.BAR_WIDTH+self.BAR_SPACING) * i,
                       self.rect.top + self.BAR_SPACING,
                       self.BAR_WIDTH,
                       self.BAR_HEIGHT
                       )
                )
        
