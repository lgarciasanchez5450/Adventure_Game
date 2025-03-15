import Application.Game.Time as Time
import Application.Game.Camera as Camera
import pygame
import Application.Textures as Textures
import Application.Game.Time as Time
from .GameScreen.Animation import SimpleAnimation
from Constants import POSITIVE_INFINITY, PERF_VS_MEMORY, TWO_PI, BLOCK_SIZE

from Application.Game.Game_Typing import *
import numpy as np
from Utils.Math.Vector import Vector2
from Application.Game.Explosion import ExplosionParticles, PARTICLE_SPEED_THRESHOLD
import Window as Window
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
    def __init__(self, animation:CheapAnimation, vel:Vector2, time:float,friction:float):
        self.vel = vel
        self.time = time
        self.k_f = friction 
        self.anim = animation

    @property
    def pos(self):
        return self.anim.csurface.pos
    
    @property
    def csurf(self):
        return self.anim.csurface

    def update(self):
        self.time -= Time.deltaTime
        self.anim.animate()
        self.anim.csurface.pos += self.vel * Time.deltaTime
        self.vel -= self.vel * Time.deltaTime * self.k_f
    @classmethod
    def noAnimation(cls,csurf:Camera.CSurface,vel:Vector2,time:float,friction:float):
        return cls(EvenCheaperAnimation(csurf),vel,time,friction)
    
    @classmethod
    def withAnimation(cls,animation:CheapAnimation,vel:Vector2,friction:float):
        return cls(animation,vel,animation.time_per_cycle,friction)


    def draw(self):
        Camera.blit_csurface(self.anim.csurface)

class SmokeParticle:
    ROTATIONS_CACHED = (180)
    SIZES_CACHED = (50)
    smallest_size = 24
    starting_alpha = 150
    base_tex:Surface#pygame.transform.grayscale((Textures.particles_opaque['smoke']).convert())
    cached_particles:dict[int,dict[int,Surface]] = {} # size -> rot(degrees)
    initialized = False
    @classmethod
    def get_particle(cls,size:int,rot:int):
        s = cls.cached_particles[size]
        return s[(rot%360)&0b111111110].copy() #bit magic to make sure the number is always even because of when it is initialized it will be on an even number
    
    @classmethod
    def initialize_caches(cls):
        cls.base_tex = (Textures.particles_opaque['new_smoke']).convert()
        cls.base_tex.set_colorkey((0,0,0))
        for size in range(cls.SIZES_CACHED):
            size += cls.smallest_size
            sizes = cls.cached_particles[size] = {}
            curr = pygame.transform.scale(cls.base_tex,(size,size))
            for rot in range(cls.ROTATIONS_CACHED):
                rot = (rot * 360 // cls.ROTATIONS_CACHED)
                sizes[rot] = pygame.transform.rotate(curr,rot)
                

    __slots__ ='rot','alpha','pos','time','vel','size','t','state','csurf'
    def __init__(self, pos:Vector2, vel: Vector2, time: float,rot:int):
        if not SmokeParticle.initialized:
            self.initialize_caches()
            SmokeParticle.initialized = True
        self.pos = pos
        self.vel = vel
        self.time = time
        self.rot = rot
        self.alpha = float(self.starting_alpha)
        self.size = float(self.smallest_size)
        self.t = 0.0
        self.state = (self.size.__trunc__(), (self.rot * 360).__trunc__() // self.ROTATIONS_CACHED)
        self.csurf = Camera.CSurface(self.get_particle(*self.state),self.pos,(0,0))
        self.csurf.offset = (-(self.csurf.surf.get_width()//2),-(self.csurf.surf.get_height()//2))


    @staticmethod
    def speed_function(t:float):
        return 1/((t+1)**5)

    def update(self):
        self.t += Time.deltaTime
        self.size += 20 *Time.deltaTime
        if self.size > 50:
            self.size = 50
        self.rot += 30 * self.speed_function(self.t/3) * Time.deltaTime
        
        self.alpha -= 40* Time.deltaTime
        if self.alpha < 0:
            self.alpha = 0.0
        self.pos += self.speed_function(self.t) * Time.deltaTime * self.vel
        self.vel *= 1 - Time.deltaTime
        state = (self.size.__trunc__(), (self.rot * 360 // self.ROTATIONS_CACHED).__trunc__())
        if state != self.state:
            self.state = state
            self.csurf.surf = self.get_particle(state[0],state[1])
            self.csurf.offset = (-(self.csurf.surf.get_width()//2),-(self.csurf.surf.get_height()//2))
        if self.alpha == 0:
            self.time = -1

    def draw(self):
        self.csurf.surf.set_alpha(self.alpha.__trunc__())
        Camera.blit_csurface(self.csurf)

TOSKIP = 20

class Smoke:
    ROTATIONS_CACHED = 180
    SIZES_CACHED = 50
    smallest_size = 24
    starting_alpha = 150
    base_tex:Surface#pygame.transform.grayscale((Textures.particles_opaque['smoke']).convert())
    cached_particles:list[list[Surface]] = [] # size -> rot(degrees) -> Surface
    cached_offset:list[dict[int,np.ndarray]] = [] # size -> rot(degrees) -> offset(half of surface size)
    initialized = False
    @classmethod
    def get_particle(cls,size:int,rot:int):
        s = cls.cached_particles[size]
        return s[(rot%360)&0b111111110] #bit magic to make sure the number is always even because of when it is initialized it will be on an even number
    
    @classmethod
    def initialize_caches(cls):
        cls.base_tex = Textures.particles_opaque['new_smoke']
        cls.base_tex.set_colorkey((0,0,0))
        for size in range(cls.smallest_size,cls.smallest_size+cls.SIZES_CACHED,1):
            sizes = [None]*cls.ROTATIONS_CACHED #type: ignore
            offsets = [None] * cls.ROTATIONS_CACHED #type: ignore
            curr = pygame.transform.scale(cls.base_tex,(size,size))
            for i in range(cls.ROTATIONS_CACHED):
                rot = (i * 360 // cls.ROTATIONS_CACHED)
                s = sizes[i] = pygame.transform.rotate(curr,rot) #type: ignore
                offsets[i] = -np.array(s.get_size(),dtype = np.int32)//2 #type: ignore
            cls.cached_particles.append(sizes) #type: ignore
            cls.cached_offset.append(offsets) #type: ignore

    def __init__(self, particles:ExplosionParticles, time: float):
        if not Smoke.initialized:
            self.initialize_caches()
            Smoke.initialized = True
        self.particles = particles
        self.time = time
        self.rots = np.random.rand(len(particles.px)) * 360
        self.alpha = self.starting_alpha
        self.size = self.smallest_size
        self.t = 0.0
        self.csurf = Camera.CSurface(self.get_particle(self.smallest_size,0),Vector2.zero(),(0,0))
        self.csurf.offset = (-(self.csurf.surf.get_width()//2),-(self.csurf.surf.get_height()//2))
        self.drawing_positions = np.empty((particles.px.shape[0]//TOSKIP,2))


    def update(self):
        self.time -= Time.deltaTime
        self.size += Time.deltaTime * 30
        self.alpha -= Time.deltaTime * 20
        if self.size >= self.SIZES_CACHED + self.smallest_size:
            self.size = self.SIZES_CACHED + self.smallest_size-1
        self.rots += 30 * Time.deltaTime

    @staticmethod
    def alphas_function(x:Numeric) -> Numeric:
        x = np.maximum(10,x) #type: ignore
        return 150 - 1500/x
        
    def draw(self):
        self.drawing_positions[:,0] = self.particles.px[::TOSKIP] * BLOCK_SIZE  + (Camera.HALFWIDTH - Camera.camera_offset_x)
        self.drawing_positions[:,1] = self.particles.py[::TOSKIP] * BLOCK_SIZE  + (Camera.HALFHEIGHT - Camera.camera_offset_y)
        alphas = np.maximum(0,self.alphas_function(self.particles.s[::TOSKIP]))
        if np.sum(alphas) == 0:
            self.time = -1
        
        #alphas = np.maximum(0,(2*self.particles.s[::TOSKIP]).astype(int))
        #print(np.average(alphas),alphas[::50])
        s = self.cached_particles[self.size.__trunc__() - self.smallest_size]  
        s2 = self.cached_offset[self.size.__trunc__() - self.smallest_size]  
        rots = self.rots.astype(np.int32)
        rots %= 360
        rots //= 2
        for rot,alpha in zip(rots,alphas):
            s[rot].set_alpha(alpha)
        #toblit = [(s[(rot%360)&0b111111110],pos + s2[(rot%360)&0b111111110]) for pos,rot in zip(self.drawing_positions,self.rots.astype(int))]
        #toblit = []
        #for pos,rot in zip(todraw,self.rots.astype(int)):
        #for pos,rot in zip(todraw,rots):
        #    toblit.append(( s[rot],pos + s2[rot]))
        
        Window.window.world_surface.blits((s[rot],pos + s2[rot]) for pos,rot in zip(self.drawing_positions,rots))


if __name__ == '__main__':
    s = pygame.display.set_mode((1,1))


    Textures.initInThread()
    from Utils.debug import profile
    while True:
        if not Textures.done_loading:
            Textures.ready_for_next = True
        else:
            break
    Time.sleep(10)
    SmokeParticle(Vector2(0,0),Vector2.zero(),1.0,0)
    Time.sleep(10)



gravity = Vector2(0,1)

g_particles:list[Particle] = []
ng_particles:list[Particle] = []











def spawn(csurf:Camera.CSurface,time:float,vel:Vector2|None = None,has_gravity:bool = False,slows_coef:float = 1.0):
    if vel is None: vel = Vector2.zero()
    particle = Particle.noAnimation(csurf,vel,time,slows_coef)
    if (has_gravity):
        g_particles.append(particle)
    else:
        ng_particles.append(particle)

def spawn_animated(anim:CheapAnimation,vel:Vector2|None = None,has_gravity:bool = False,slows_coef:float = 1.0):
    if vel is None: vel = Vector2.zero()
    particle = Particle.withAnimation(anim,vel,slows_coef)
    if (has_gravity):
        g_particles.append(particle)
    else:
        ng_particles.append(particle)

def spawn_hit_particles(pos:Vector2,time:float,amount:int = 5):
    for x in range(amount):
        spawn(Camera.CSurface.inferOffset(Textures.particles_opaque['death'],pos+Vector2.random()/10),time,Vector2.random())

def spawn_smoke_particle(pos:Vector2,vel:Vector2,rot:int):
    default_time = 20.0
    ng_particles.append(SmokeParticle(pos,vel,default_time,rot)) #type: ignore

def spawn_smoke(particles,time:float):
    ng_particles.append(Smoke(particles,time)) #type: ignore

def update_list(myList:list[Particle],has_gravity:bool):
    to_remove = []
    for index,particle in enumerate(myList):
        particle.update()
        if particle.time < 0:
            to_remove.append(index)
            continue
        if has_gravity:
            particle.vel += gravity * Time.deltaTime
        
    #we can actually do this because it is being iterated over backwards
    for index in to_remove.__reversed__():
        myList.pop(index)

def update():
    update_list(ng_particles,False)
    update_list(g_particles,True)
   




   
def draw():
    for particle in ng_particles:
        particle.draw()
    for particle in g_particles:
        particle.draw()


