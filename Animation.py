import Time
import pygame
import Camera
class Animation:
    __slots__ = 'csurface','frames','anim_fps','_frame_in_state','max_frames_in_state','direction','time','frames_in_state','frame_in_frame','surf','state','on_animation_done','previous_frame_in_state'
    def __init__(self,csurf:Camera.CSurface):
        self.csurface = csurf
        self.frames:dict[str,list[pygame.Surface]] = {}
        self.anim_fps:dict[str,float] = {}
        self._frame_in_state:int = 0
        self.max_frames_in_state:int = 0
        self.direction = 'right'
        self.time:float = 0.0
        self.frames_in_state = 0
        self.frame_in_frame = 0
        self.on_animation_done = lambda : 0
    def add_state(self,state:str,fps:float,frames_right:list,frames_left:list):
        self.anim_fps[state] = fps
        self.frames.update({state+'_right':frames_right,state+'_left':frames_left})
        

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
        if self._frame_in_state == self.max_frames_in_state-1: self.on_animation_done() #might be unneccesary
        
        if self.previous_frame_in_state == self.max_frames_in_state - 1 and self._frame_in_state == 0 == self.frame_in_frame: self.on_animation_done()

class SimpleAnimation:
    __slots__ = ('csurface','frames','fps','time','_frame_in_state','max_frames_in_state','surf')
    def __init__(self,csurf:Camera.CSurface,fps:int,frames:list):
        self.csurface = csurf
        if not isinstance(frames,list):
            frames = [frames]
        self.frames:list[pygame.Surface] = frames
        self.fps = fps
        self.time:float = 0.0
        self._frame_in_state = 0
        self.max_frames_in_state = len(self.frames)

    def reset(self):
        self.time = 0.0
        self._frame_in_state = 0
        self.csurface.surf = self.frames[0]
        
    def animate(self):
        self.time += self.fps*Time.deltaTime
        self._frame_in_state = (self.time % self.max_frames_in_state).__trunc__() # might be faster if we just increment then catch with an if statement
        self.surf = self.frames[self._frame_in_state]
        self.csurface.surf = self.surf
        


if __name__ == '__main__':
    from pympler.asizeof import asizeof
    print(asizeof(SimpleAnimation(Camera.NullCSurface,10,[])))