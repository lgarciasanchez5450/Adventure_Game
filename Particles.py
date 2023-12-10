import Time
import game_math
import Camera
import pygame
import Textures
import Time
from Animation import SimpleAnimation
from Constants import POSITIVE_INFINITY
from Game_Typing import *
if TYPE_CHECKING:
    from general_manager import GameObject

class CheapAnimation:
    __slots__ = 'frames','fps','time','max_frames','csurface'
    def __init__(self,csurf:Camera.CSurface,images:tuple[Surface,...], fps:float):
        assert len(images), 'cant have empty images list!'
        self.frames = images
        self.fps = fps
        self.time = 0.0
        self.max_frames = (images).__len__()
        self.csurface = csurf


    @property
    def time_per_cycle(self) -> float:
        '''Seconds it takes to complete all frames'''
        if self.fps == 0:
            return POSITIVE_INFINITY
        return self.max_frames / self.fps


    def animate(self):
        self.time += self.fps*Time.deltaTime
        self.csurface.surf = self.frames[(self.time % self.max_frames).__trunc__()]

class EvenCheaperAnimation(CheapAnimation):
    def __init__(self,csurface):
        self.csurface = csurface
    def animate(self): pass

class Particle:
    __slots__ = 'vel','time', 'k_f','anim'
    def __init__(self, animation:CheapAnimation, vel:game_math.Vector2, time:float,friction:float):
        self.vel = vel
        self.time = time
        self.k_f = friction 
        self.anim = animation

    def update(self):
        self.anim.animate()

    @classmethod
    def noAnimation(cls,csurf:Camera.CSurface,vel:game_math.Vector2,time:float,friction:float):
        return cls(EvenCheaperAnimation(csurf),vel,time,friction)
    
    @classmethod
    def withAnimation(cls,animation:CheapAnimation,vel:game_math.Vector2,friction:float):
        return cls(animation,vel,animation.time_per_cycle,friction)

gravity = game_math.Vector2(0,1)

g_particles:list[Particle] = []
ng_particles:list[Particle] = []


def spawn(csurf:Camera.CSurface,time:float,vel:game_math.Vector2|None = None,has_gravity:bool = False,slows_coef:float = 1.0):
    if vel is None: vel = game_math.Vector2.zero
    particle = Particle.noAnimation(csurf,vel,time,slows_coef)
    if (has_gravity):
        g_particles.append(particle)
    else:
        ng_particles.append(particle)

def spawn_animated(anim:CheapAnimation,vel:game_math.Vector2|None = None,has_gravity:bool = False,slows_coef:float = 1.0):
    if vel is None: vel = game_math.Vector2.zero
    particle = Particle.withAnimation(anim,vel,slows_coef)
    if (has_gravity):
        g_particles.append(particle)
    else:
        ng_particles.append(particle)

def spawn_hit_particles(pos:game_math.Vector2,time:float,amount:int = 5):
    for x in range(amount):
        spawn(Camera.CSurface.inferOffset(Textures.particles_opaque['death'],pos+game_math.Vector2.random/10),time,game_math.Vector2.random)

def update_list(myList:list[Particle],has_gravity:bool):
    to_remove = []
    for index,particle in enumerate(myList):
        particle.time -= Time.deltaTime
        if particle.time < 0:
            to_remove.append(index)
            continue
        particle.update()
        p:game_math.Vector2 = particle.anim.csurface.pos 
        v:game_math.Vector2 = particle.vel
        p += v * Time.deltaTime
        if has_gravity:
            v += gravity * Time.deltaTime
        
        v -= v * Time.deltaTime * particle.k_f
    #we can actually do this because it is being iterated over backwards
    for index in to_remove.__reversed__():
        myList.pop(index)
def update():
    update_list(ng_particles,False)
    update_list(g_particles,True)
   







   
def draw():
    for particle in ng_particles:
        Camera.blit_csurface(particle.anim.csurface)
    for particle in g_particles:
        Camera.blit_csurface(particle.anim.csurface)


