import Animation
import Camera
import Input
from game_math import Collider,Vector2
from typing import Callable, Literal
from pygame import Surface
from Time import Stopwatch
from Constants.Generation import BLOCK_SIZE,HALF_BLOCK_SIZE

class Button:
    def __init__(self,center:Vector2,size:Vector2):
        self.center = center.copy()
        self.size = size.copy()
        self.OnPressFunc:Callable[[],None] = lambda : None
        self.OnReleaseFunc:Callable[[],None] = lambda : None
        self.inner_csurf = Camera.CSurface(Surface((self.size * BLOCK_SIZE).tupled_ints),Vector2.zero,(0,0))
        self.inner_csurf.surf.fill('red')
        self.csurf = Camera.CSurface(Surface((self.size * BLOCK_SIZE).tupled_ints),self.center,(-self.size * HALF_BLOCK_SIZE).tupled_ints)
        self.animation:Animation.SimpleAnimation = Animation.SimpleAnimation(self.inner_csurf,0,[self.inner_csurf.surf])
        self.state:Literal['up','down','idle'] = 'up'

        # Make collider
        topleft = self.center - self.size/2
        self.collider = Collider(topleft.x,topleft.y,size.x,size.y)
        
        # Private variables
        self.onLoad()
        self.gray_surface = Surface((self.size * BLOCK_SIZE).tupled_ints)
        self.gray_surface.set_alpha(180)
        self.gray_surface.fill((100,100,100))


    def setOnPress(self,func:Callable[[],None]):
        self.OnPressFunc = func
        return self
    
    def setOnRelease(self,func:Callable[[],None]):
        self.OnReleaseFunc = func
        return self
    
    def setCustomFrames(self,frames:tuple[Surface,...],fps:float = 0):
        self.animation.setFrames(frames,fps) 
        return self

    def onLoad(self):
        Camera.add(self.csurf)
    
    def onLeave(self):
        Camera.remove(self.csurf)
    
    def update(self) -> None: 
        self.animation.animate() #update the animator
        #copy inner csurf to outer one while applying all transformations
        if self.collider.collide_point_inclusive(Camera.world_position_from_normalized(Input.m_pos_normalized)):
            if Input.m_d1:
                self.OnPressFunc()
            elif Input.m_u1:
                self.OnReleaseFunc()
            self.state = 'down' if Input.m_1 else 'idle'            
        else:
            self.state = 'up'
        self.csurf.surf.blit(self.inner_csurf.surf,(0,0)) 
        if self.state == 'idle':
            self.csurf.surf.blit(self.gray_surface,(0,0))

class Picture:
    def __init__(self,center:Vector2,size:Vector2):
        self.center = center.copy()
        self.size = size.copy()
        self.csurf = Camera.CSurface(Surface((self.size).tupled_ints),self.center,(-self.size//2).tupled_ints)
        self.animation:Animation.SimpleAnimation = Animation.SimpleAnimation(self.csurf,0,[self.csurf.surf])
        self.state:Literal['up','down','idle'] = 'up'

        # Make collider
        
        # Private variables
        Camera.add(self.csurf)

    def onLeave(self):
        Camera.remove(self.csurf)

    def update(self):
        self.animation.animate()

    def setCustomFrames(self,frames:tuple[Surface,...],fps:float = 0):
        self.animation.setFrames(frames,fps) 
        return self