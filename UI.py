from typing import Any
import pygame
from Constants import *
if __name__ == "__main__":
    display = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT),pygame.OPENGL| pygame.DOUBLEBUF) # can be Resizable with no problems
import Camera
from Constants import HEIGHT, WIDTH
import Time
from game_math import Vector2, Collider,ones,deque, Vector2Int
import Input
from Game_Typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from Items import Item
tex_location = 1

class UI:
    __slots__ = 'tex_location','center','size','surface','surface_size','tex','program','render_object','topleft','collider','thingy','relative_mouse_position_normalized','rel_mouse_pos'
    def __init__(self,surface_size:tuple|list = (WIDTH,HEIGHT),screen_offset:tuple|list = (0,0),screen_size = (1,1)):
        global tex_location
        
        self.tex_location = tex_location
        self.center = Vector2(*screen_offset)
        self.size = Vector2(*screen_size)
        self.surface = pygame.Surface(surface_size)
        self.surface_size = Vector2(*surface_size)
        self.tex = Camera.surf_to_texture(self.surface)
        self.program,self.render_object = Camera.create_new_render_object('shaders/everything.vert','shaders/ui.frag',screen_size,screen_offset)
        self.topleft = Vector2(screen_offset[0] - screen_size[0],screen_offset[1]-screen_size[1])
        self.tex.use(tex_location)
        self.program['tex'] = tex_location
        tex_location += 1
        self.collider = Collider(self.topleft.x,self.topleft.y,screen_size[0]*2,screen_size[1]*2)
        self.thingy = Vector2(*screen_size).inverse

    def _(self):
        pass

    def onResize(self,width,height):
        pass

    def update(self):
        self.surface.fill('grey')
        self.relative_mouse_position_normalized = (Input.m_pos_normalized - self.center).vector_mul(self.thingy)
        self.rel_mouse_pos = (self.relative_mouse_position_normalized+ones).vector_mul(self.surface_size/2)
        #if self.collider.collide_point_inclusive(Input.m_pos_normalized.tuple): 
    
    def draw(self):
        self.tex.write(self.surface.get_view('1'))
        self.render_object.render()

    def __del__(self):
        self.tex.release()
        self.render_object.release()
        self.program.release()

class InScreenUI:
    #__slots__ = 'size','topleft','surface','surface_size','center','collider','thingy','relative_mouse_position_normalized','rel_mouse_pos'
    def __init__(self, center:Vector2Int,size:tuple[int,int]):
        self.size = Vector2Int(*size)
        #normal screen units
        self.topleft = center - Vector2Int.new_from_tuple(size)//2
        self.surface = pygame.Surface(size)
        self.surface_size = Vector2.new_from_tuple(size)
        #normalized units
        self.center = Vector2(center.x/WIDTH,center.y/HEIGHT)
        normalized_topleft = center - Vector2Int(HALFWIDTH,HALFHEIGHT) - Vector2Int.new_from_tuple(size)#center is in pixels
        normalized_topleft = Vector2(normalized_topleft.x/WIDTH, normalized_topleft.y/HEIGHT)
        normalized_size = Vector2.new_from_tuple(size) # size is in pixels
        normalized_size.x /= WIDTH
        normalized_size.y /= HEIGHT
        self.collider = Collider(normalized_topleft.x,normalized_topleft.y,normalized_size.x,normalized_size.y)
        self.thingy = normalized_size.inverse

    def update(self):
        self.surface.fill('grey')
        if self.collider.collide_point_inclusive(Input.m_pos_normalized.tuple): 
            self.relative_mouse_position_normalized = (Input.m_pos_normalized - self.center).vector_mul(self.thingy)
            self.rel_mouse_pos = (self.relative_mouse_position_normalized+ones).vector_mul(self.surface_size/2)


    def draw(self,surface:pygame.Surface):
        surface.blit(self.surface,self.topleft.tuple)

class ItemDescriptionUI:
    CONTENT_SPACING:int = 10
    BACKGROUND_COLOR = (30,30,30,220)
    BORDER_COLOR = (20,30,100,220)
    def __init__(self):
        self.name_font = pygame.font.SysFont("Courier",15,True)
        self.name_color = (255,255,255,255)
        self.description_font = pygame.font.SysFont("Arial",14)
        self.description_color = 'grey'
        self.lore_font = pygame.font.SysFont("Arial",12)
        self.lore_color = (200,200,200,255)
        self.pos = Vector2.zero
        self.width = 200 # pixels
        self.content_width = 180
        self.content_left = (self.width - self.content_width) // 2
        assert self.width > 0 and self.content_width > 0, 'bruh this doesnt even make sense'
        assert self.content_left >0, 'width must be greater than content width by more than 1 !!!'
        self.item:Optional['Item']
        self.size = Vector2(self.width,0)
        self.name:pygame.Surface
        self.description:pygame.Surface
        self.lore:pygame.Surface
        self.surf = pygame.Surface((self.width,0),pygame.SRCALPHA)
        self.surf.fill(self.BACKGROUND_COLOR)


    def setItem(self,item:Optional['Item']): 
        self.item = item
        if self.item is None: return
        self.name = self.name_font.render(self.item.name,True,self.name_color,wraplength=self.content_width)
        self.description = self.description_font.render(self.item.description,True,self.description_color,wraplength=self.content_width)
        self.lore = self.lore_font.render(self.item.lore,True,self.lore_color,wraplength=self.content_width)
        self.size.y = 20#self.name.get_height() + self.description.get_height() + self.lore.get_height() + 20 #10 for each spacing above and below all the texts
        self.size.y += self.name.get_height()
        if not (self.item.description or self.item.lore):
            self.size.x = self.name.get_width() + self.CONTENT_SPACING * 2 # 10 for each side!!
        else: 
            self.size.x = self.width

        if self.item.description:
            self.size.y += self.CONTENT_SPACING + self.description.get_height()
        if self.item.lore:
            self.size.y += self.CONTENT_SPACING + self.lore.get_height()
        self.surf = pygame.Surface(self.size.tuple,pygame.SRCALPHA)

        self.surf.fill(self.BACKGROUND_COLOR)
        self._setSurfaceFrame()
        self.surf.blits([
            (self.name,(self.content_left,self.CONTENT_SPACING)),
            (self.description,(self.content_left,self.name.get_height() + self.CONTENT_SPACING * 2)),
            (self.lore,(self.content_left, self.size.y - self.lore.get_height()-self.CONTENT_SPACING)),
        ],doreturn=False
        )

    def _setSurfaceFrame(self):
        r = pygame.Rect((0,0,2,2))
        big_rect = self.surf.get_rect()
        pygame.draw.rect(self.surf,self.BORDER_COLOR,big_rect,2)
        pygame.draw.rect(self.surf,(0,0,0,0),r)
        r.topright = big_rect.topright
        pygame.draw.rect(self.surf,(0,0,0,0),r)
        r.bottomleft = big_rect.bottomleft
        pygame.draw.rect(self.surf,(0,0,0,0),r)
        r.bottomright = big_rect.bottomright
        pygame.draw.rect(self.surf,(0,0,0,0),r)
    def update(self):
        pass # TODO add the cool scrolling function for reading long descriptions soon

    def draw(self,surface:pygame.Surface,pos:Vector2Int): 
        if self.item is None: return
        surface.blit(self.surf,pos.tuple)

itemDescriptor = ItemDescriptionUI()

class EmtpyUI(UI):
    __slots__ = tuple()
    def __init__(self,*args,**kwargs): pass
    def __setattr__(self, __name: str, __value: Any) -> None: pass
    def __delattr__(self, __name: str) -> None: pass
    def update(self,*args,**kwargs): pass
    def draw(self): pass
    def __del__(self): pass

class DebugUI(UI):
    def __init__(self):
        super().__init__((WIDTH*.1,HEIGHT*.1),(-.9,.9),(.1,.1))
        self.font = pygame.font.SysFont('Arial',30,1)

    def update(self):
        self.surface.fill((0,0,0))
        self.surface.blit(self.font.render(str(Time.get_frameRateInt()),True,(255,255,255)),(0,0))

Null = EmtpyUI()

showingUIs:deque[UI] = deque([Null],maxlen=1)
inScreenUI:deque[InScreenUI] = deque([Null],maxlen=1) #type: ignore

