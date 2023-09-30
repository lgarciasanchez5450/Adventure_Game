import Time
import game_math
import Camera
import pygame
import Textures
import Time
from Animation import SimpleAnimation

class Cheap_Animation:
    def __init__(self,pos,images:list[pygame.Surface]|tuple,fps:int,onDone):
        self.images = images
        self.onDone = onDone
        #self.total_time = len(images) * 1/fps
        self.fps = fps
        self.time = 0.0
        self.frame:int = 0
        self.inv_fps = 1/fps
        self.max_frames = len(images)
        self.csurf = Camera.CSurface(self.images[0],pos,(-self.images[0].get_width()//2,-self.images[0].get_height()//2))
        self.done = False


    def onDone(self): ...


    def animate(self):
        if self.done:return

        self.time += Time.deltaTime
        if self.time > self.inv_fps:
            self.time -= self.inv_fps
            self.frame += 1
            if self.frame == self.max_frames:
                self.done= True
                self.onDone()
                return
            self.csurf.surf = self.images[self.frame]
            
        



gravity = game_math.Vector2(0,1)

particles = []
anim_particles = []
after_particles = []
to_remove_anim = []
def toRemove(anim):
    return lambda : to_remove_anim.append(anim)
def spawn(pos:game_math.Vector2,vel,surf,time:float|int,offset = (0,0),has_gravity:bool = False,slows_coef = 1):
    particles.append([Camera.CSurface(surf,pos.copy(),offset),vel,time,has_gravity,slows_coef])

def spawn_animated(anim:Cheap_Animation,has_gravity:bool = False,slow_coef:float|int = 1):
    anim.onDone = toRemove(anim)
    anim_particles.append([anim,has_gravity,slow_coef])

def after_spawn(pos:game_math.Vector2,vel,surf,time:float|int,offset = (0,0),has_gravity:bool = False,slows_coef = 1):
    after_particles.append([Camera.CSurface(surf,pos.copy(),offset),vel,time,has_gravity,slows_coef])


def spawn_hit_particles(pos:game_math.Vector2,time:float,amount:int = 5):
    for x in range(amount):
        spawn(pos+game_math.Vector2.random/10,game_math.Vector2.random,Textures.texture['death.png'],time,(0,0),True)

def update_list(myList:list):
    to_remove = []
    for index,particle in enumerate(myList):
        particle[2] -= Time.deltaTime
        if particle[2] < 0:
            to_remove.append(index)
            continue
        p:game_math.Vector2 = particle[0].pos 
        v:game_math.Vector2 = particle[1]
        p += v * Time.deltaTime
        if particle[3]:
            v += gravity * Time.deltaTime
        
        v -= v * Time.deltaTime * particle[4]
    #we can actually do this because it is being iterated over backwards
    for index in to_remove.__reversed__():
        myList.pop(index)
def update():
    update_list(particles)
    update_list(after_particles)
    for particle in (anim_particles):
        anim:Cheap_Animation = particle[0]
        #p = anim.csurface.pos
        anim.animate()
    for anim in to_remove_anim.__reversed__():
        for index,particle in enumerate(anim_particles):
            if particle[0] is anim:
                anim_particles.pop(index)
                break







   
def draw():
    for particle in particles:
        Camera.blit_csurface(particle[0])


def after_draw():
    for particle in after_particles:
        Camera.blit_csurface(particle[0])

def anim_draw():
    for particle in anim_particles:
        Camera.blit_csurface(particle[0].csurf)

