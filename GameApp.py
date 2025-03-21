import time
import pygame
import moderngl as mgl
from pygame import Window
from pygame.time import Clock
import pygame.constants as const
pygame.font.init()
from Scene import Scene
from Scripts.ProgramManager import ProgramManager
from Utils.debug import Tracer


class Engine:
    def __init__(self,window:Window) -> None:
        # MGL context
        self.window = window
        self.ctx = mgl.create_context()
        self.ctx.enable(mgl.CULL_FACE|mgl.DEPTH_TEST)
        # Time variables
        self.clock = Clock()
        self.time = Time()
        self.tracer = Tracer()

        # Project handler
        self.program_manager = ProgramManager(self.ctx)
        
        self.running = False

    def Init(self):
        self.scenes:dict[str,Scene] = {'scene1':Scene(self,self.window)}
        self.active_scene:Scene = list(self.scenes.values())[0]

    def start(self):
        self.window.get_surface()
        self.Init()
        # rss_base = psutil.Process().memory_info().rss #memory(rss from psutil) used by python only importing python and moderngl

        # pygame.display.set_caption(f'{self.active_scene.get_memory()/1_000_000:.2f} MB')
        # pygame.display.set_caption(f'{(psutil.Process().memory_info().rss-rss_base)/1_000_000} MB')
        self.running = True 
        self.time.start()
        self.active_scene.start()
        while self.running:
            for event in pygame.event.get():
                if event.type == const.WINDOWCLOSE:
                    self.running = False
                elif event.type== const.KEYDOWN:
                    if event.key == const.K_p:
                        self.tracer.running = True
                elif event.type== const.KEYUP:
                    if event.key == const.K_p:
                        self.tracer.running = False
            self.keys = pygame.key.get_pressed()
            self.time.update()
            self.active_scene.update()
            self.active_scene.draw()
            self.window.flip()
            self.clock.tick(60)
        self.tracer.show()


        
class Time:
    __slots__ = 'dt','fixedDt','_prevTime','time','timeScale','realTime','_startTime','unscaledDeltaTime','frame'
    def __init__(self) -> None:
        self.dt = 0
        self.timeScale = 1
        self.fixedDt = 0.1


    def start(self):
        self.time = 0
        self.realTime = 0
        self.unscaledDeltaTime = 0
        self.frame = 0
        self._prevTime = self._startTime = time.perf_counter()

    
    def update(self):
        t = time.perf_counter()
        u = self.unscaledDeltaTime = (t - self._prevTime)
        self.dt = u * self.timeScale
        self.time += self.dt
        self._prevTime = t
        self.realTime = t - self._startTime
        self.frame += 1

    def getFPS(self):
        return 1 / self.unscaledDeltaTime if self.unscaledDeltaTime else 0

class GameApp: 
    def __init__(self) -> None:
        self.window = Window('hello',(800,600),opengl=True,resizable=True)
        self.engine = Engine(self.window)  
    
    def run(self):
        return self.engine.start()
   
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
    GameApp().run()
