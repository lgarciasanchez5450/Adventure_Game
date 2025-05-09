import os
import time
import pygame
import moderngl as mgl
from pygame import Window
from pygame import Event
from pygame import Surface
from pygame.time import Clock
from pygame import constants as const
from GLScene import GLScene
from Scripts.ProgramManager import ProgramManager
from FBO import FBO

class Input:
    _iterating_i:int
    mx:int
    my:int

    events:list[Event]
    __slots__ = '_iterating_i','mx','my','events'
    def __init__(self):
        self._iterating_i = -1

    def gather(self,eventtype = None,pump: bool = True, exclude = None):
        self.events.extend(pygame.event.get(eventtype,pump,exclude))

    def __iter__(self):
        i = 0
        j = 0        
        ev = self.events
        for i in range(len(ev)):
            n = yield ev[i]
            
    @property
    def mpos(self): return self.mx,self.my

# class Engine:
#     def __init__(self,output:Surface) -> None:
#         # MGL context
#         self.screen = output
#         self.ctx = mgl.create_context()
#         self.ctx.enable(mgl.CULL_FACE|mgl.DEPTH_TEST)
#         # Time variables
#         self.clock = Clock()
#         self.time = Time()
#         self.t_last_update = 0

#         self.program_manager = ProgramManager(self.ctx)
#         self.running = False

#     def start(self): 
#         self.running = True
#         self.t_last_update = time.perf_counter()

#     def update(self,events:list[Event]): 
#         assert self.running
#         t_cur = time.perf_counter()
#         self.dt = t_cur = self.t_last_update
#         self.t_last_update = t_cur


#     def draw(self): 
#         assert self.running

#     def stop(self):
#         self.running = False


class GLEngine:
    def __init__(self,output:mgl.Framebuffer) -> None:
        # MGL context
        self.screen = output
        self.ctx = mgl.get_context()
        self.ctx.enable(mgl.CULL_FACE|mgl.DEPTH_TEST)
        # Time variables
        self.clock = Clock()
        self.t_last_update = 0

        self.program_manager = ProgramManager(self.ctx)
        self.running = False

        self.scenes:dict[str,GLScene] = {}
        for filename in os.listdir('./Scenes'):
            if filename.endswith('.scene'):
                name = filename.removesuffix('.scene')
                if name in self.scenes:
                    raise NameError(f'Error Loading Scenes: There are two scenes with the name: {name}')
                fqn = os.path.abspath(os.path.join('./Scenes',filename))
                self.scenes[name] = GLScene.load(fqn,self.ctx.screen)

    def start(self):
        self.running = True
        self.t_last_update = time.perf_counter()
        self.scene = self.scenes['test']

    def update(self,events:list[Event]): 
        assert self.running
        t_cur = time.perf_counter()
        self.dt = t_cur = self.t_last_update
        self.t_last_update = t_cur
        self.scene.update(events)

    def draw(self):
        assert self.running
        self.scene.draw(self.ctx)

    def stop(self):
        self.running = False


class GameApp: 
    def __init__(self) -> None:
        self.window = Window('hello',(1,1),fullscreen_desktop=True,opengl=True,resizable=True)
        self.ctx = mgl.create_context()
        self.engine = GLEngine(self.ctx.screen)  

    
    def run(self):
        self.engine.start()
        self.running = True
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        if event.mod&pygame.K_LCTRL:
                            self.running = False

            if self.engine.running:
                self.engine.update(events)
                self.engine.draw()

            self.window.flip()
    
if False:
    from pygame import display
    class Window:
        def __init__(self,name:str,size:tuple[int,int],*,  fullscreen: bool = False,opengl: bool = False,resizable: bool = False):
            display.set_mode(size,(const.OPENGL*opengl)|(const.RESIZABLE*resizable)|(const.FULLSCREEN*fullscreen)|(const.DOUBLEBUF*opengl))
            self.title = name

        def get_surface(self):
            return display.get_surface()
        
        @property
        def size(self):
            return display.get_window_size()
        
        def flip(self):
            display.flip()

        @property
        def title(self):
            return display.get_caption()
        
        @title.setter
        def title(self,newVal:str):
            display.set_caption(newVal)

        @property
        def mouse_grabbed(self):
            return pygame.event.get_grab()
        
        @mouse_grabbed.setter
        def mouse_grabbed(self,newVal:bool):
            return pygame.event.set_grab(newVal)
        @property
        def grab_mouse(self):
            return pygame.event.get_grab()
        
        @grab_mouse.setter
        def grab_mouse(self,newVal:bool):
            return pygame.event.set_grab(newVal)
            

if __name__ == '__main__':
    pygame.init()
    GameApp().run()
