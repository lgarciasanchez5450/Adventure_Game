from typing import Any
import pygame
from Constants import *
if __name__ == "__main__":
    display = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT),pygame.OPENGL| pygame.DOUBLEBUF) # can be Resizable with no problems
import Camera
from Constants import HEIGHT, WIDTH
import Time
from game_math import cache,Vector2, Collider,ones,deque
import Input


tex_location = 1
class EmtpyUI:
    def __init__(self,*args,**kwargs):
        pass

    def __setattr__(self, __name: str, __value: Any) -> None:
        pass


    def __delattr__(self, __name: str) -> None:
        pass
    def update(self,*args,**kwargs):
        pass

    def draw(self):
        pass


class UI:
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

    def _():
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


class DebugUI(UI):
    def __init__(self):
        super().__init__((WIDTH*.1,HEIGHT*.1),(-.9,.9),(.1,.1))
        self.font = pygame.font.SysFont('Arial',30,1)

    def update(self):
        self.surface.fill((0,0,0))
        self.surface.blit(self.font.render(str(Time.get_frameRateInt()),1,(255,255,255)),(0,0))

class Fake_Inventory:
    spaces:int

Null = EmtpyUI()

showingUIs:deque[UI] = deque([Null],maxlen=1)


