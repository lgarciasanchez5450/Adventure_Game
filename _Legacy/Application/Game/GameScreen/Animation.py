from ..Constants import POSITIVE_INFINITY
import Application.Game.Time as Time
import pygame
import Application.Game.Camera as Camera
class Animation:
    '''A full fledged Animation class with hooks for onAnimation done and lots of customizability, if a less feature-rich animation is needed use SimpleAnimation'''
    __slots__ = 'csurface','frames','anim_fps','_frame_in_state','max_frames_in_state','direction','time','frames_in_state','frame_in_frame','surf','state','on_animation_done','previous_frame_in_state'
    def __init__(self,csurf:Camera.CSurface):
        self.csurface = csurf
        self.frames:dict[str,tuple[pygame.Surface,...]] = {}
        self.anim_fps:dict[str,float] = {}
        self._frame_in_state:int = 0
        self.max_frames_in_state:int = 0
        self.direction = 'right'
        self.time:float = 0.0
        self.frames_in_state = 0
        self.frame_in_frame = 0
        self.on_animation_done = lambda : None

    def add_state(self,state:str,fps:float,frames_right:tuple[pygame.Surface,...],frames_left:tuple[pygame.Surface,...]|None = None):
        self.anim_fps[state] = fps
        self.frames[state+'_right'] = frames_right
        if frames_left is not None:
           self.frames[state+'_left'] = frames_left


    def set_state(self,state:str) -> None:  
        self.time:float = 0.0
        self.state = state
        self._frame_in_state = 0
        self.frames_in_state = 0
        self.frame_in_frame = 0
        self.max_frames_in_state = len(self.frames['_'.join([state,self.direction])])
        self.surf:pygame.Surface = self.frames["_".join([self.state,self.direction])][self._frame_in_state]

    def animate(self):
        self.time += self.anim_fps[self.state]*Time.deltaTime
        self.previous_frame_in_state = self._frame_in_state
        self._frame_in_state = (self.time % self.max_frames_in_state).__trunc__() # might be faster if we just increment then catch with an if statement
        
        if self.previous_frame_in_state != self._frame_in_state: self.frame_in_frame = 0
        else: self.frame_in_frame += 1
        self.surf:pygame.Surface = self.frames["_".join([self.state,self.direction])][self._frame_in_state]
        self.csurface.surf = self.surf
        self.frames_in_state +=1
        #if self._frame_in_state == self.max_frames_in_state-1: self.on_animation_done() #might be unneccesary
        
        if self.previous_frame_in_state == self.max_frames_in_state - 1 and self._frame_in_state == 0 == self.frame_in_frame: self.on_animation_done()


class SimpleAnimation:
    '''This Animation Class is meant to provide a simpler interface and be faster than the normal Animation class'''
    __slots__ = 'csurface','frames','fps','time','_frame_in_state','max_frames_in_state','surf'
    def __init__(self,csurf:Camera.CSurface,fps:float,frames:pygame.Surface|tuple[pygame.Surface,...]):
        self.csurface = csurf
        if not isinstance(frames,(list,tuple)):
            frames = (frames,)
        self.setFrames(frames,fps)

    def setFrames(self,frames:tuple[pygame.Surface,...],fps:float) -> None:
        self.frames = tuple(frames)
        self.fps = fps
        self.max_frames_in_state = len(self.frames)
        self.csurface.surf = self.surf = frames[0]
        self.time:float = 0.0
        self._frame_in_state:int = 0

    @property
    def time_per_cycle(self) -> float:
        '''Seconds it takes to complete all frames'''
        if self.fps == 0:
            return POSITIVE_INFINITY
        return self.max_frames_in_state / self.fps

    def reset(self):
        self.time = 0.0
        self._frame_in_state = 0
        self.csurface.surf = self.frames[0]
        
    def animate(self):
        self.time += self.fps*Time.deltaTime
        self._frame_in_state = (self.time % self.max_frames_in_state).__trunc__() # might be faster if we just increment then catch with an if statement
        self.surf = self.frames[self._frame_in_state]
        self.csurface.surf = self.surf


    def copyTo(self,other) -> None:
        assert isinstance(other,SimpleAnimation)
        other.setFrames(self.frames,self.fps)
        other.time = self.time
        other.surf = self.surf
        other._frame_in_state = self._frame_in_state

        


if __name__ == '__main__':
    from pympler.asizeof import asizeof
    print(asizeof(SimpleAnimation(Camera.NullCSurface,10,(Camera.NullCSurface.surf,))))
    t = Animation(Camera.NullCSurface)
    #t.add_state('left',10,[],[])
    print(asizeof(t))
