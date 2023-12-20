from game_math import Vector2
import numpy as np
#from Game_Typing import TYPE_CHECKING
from GameObject import GameObject
from Game_Typing import Moves
import Time
from Constants.DamageTypes import EXPLOSION_DAMAGE
#from jax import jit as jaxjit
from numba import njit
from debug import profile
#PARTICLES_TO_SIMULATE = 1024
PARTICLES_TO_SIMULATE = 2_000
PARTICLE_SPEED_THRESHOLD = .5 #in units/second (not inclusive, meaining if particles are exactly at 0.5 speed then they will not be counted)
PARTICLES_THRESHOLD = 5
DYNAMIC_ENTITY_VELOCITY_MODIFIER = 0.2 # a value of 1 will completely cancel out the damage from explosion when going directly away from explosion
PARTICLE_TOUCHING_DRAG = 20.0 #how much the particles will slow down when touching an object
FALLOFF = 0.01

# cache variables, dont change!
ONE_MINUS_FALLOFF = 1 - FALLOFF # 

Time.deltaTime = 1/60
@njit(boundscheck = False)
def _dmg_to_ent(dx,dy,hit_size,speed_changes,energy_per_particle,valid_particles,energy,s)->float:
    dists = np.hypot(dx,dy) #calc dinstance of each particle to the obj
    dists -= hit_size #subtract a margin of error due to timesteps
    dists = np.minimum(dists,0)  #get rid of all particles which arent close enough

    #quick intermission to slow down the objects which are being collided
    inv = 1 / hit_size
    speed_changes *= (hit_size+dists) * inv

    #resume the normal stuff
    hits = np.sum(np.logical_and(dists , valid_particles)) #count how many are colliding with obj
    if  hits < PARTICLES_THRESHOLD : return 0 #if less than 5 are colliding with us than we say that its just a stray particle and we dont count it
    damage = hits * (energy_per_particle) * 10 - np.sum(np.multiply(dists,s)) * energy  #we need to negate the np.sum because dists are all negitve
    return damage

@njit(boundscheck = False)
def _e_update(px,py,vx,vy,dt,s,valids,m):
    np.hypot(vx,vy,s)
    valids[s < PARTICLE_SPEED_THRESHOLD] = 0
    t = np.maximum(ONE_MINUS_FALLOFF-s * (m*dt) ,0.0)
    vx *= t
    vy *= t
    px += vx * dt
    py += vy * dt

class ExplosionParticles:
    __slots__ = 'm','px','py','vx','vy','valid_particles','s'
    def __init__(self,pos:Vector2,energy:float,m:float):
        self.m = m
        self.px = np.empty(PARTICLES_TO_SIMULATE,dtype = np.float32)
        self.py = np.empty(PARTICLES_TO_SIMULATE,dtype = np.float32)
        self.px[:] = pos.x
        self.py[:] = pos.y
        self.vx = np.cos(np.arange(PARTICLES_TO_SIMULATE,dtype = np.float32) * (6.283185307197959 / PARTICLES_TO_SIMULATE)) * energy
        self.vy = np.sin(np.arange(PARTICLES_TO_SIMULATE,dtype = np.float32) * (6.283185307197959 / PARTICLES_TO_SIMULATE)) * energy
        self.valid_particles = np.ones(PARTICLES_TO_SIMULATE,dtype = np.int32) # an array contiaining a 0 if particle is below speed threshold or 1 if they are above
        self.s = np.empty(PARTICLES_TO_SIMULATE,dtype = np.float32)
        np.hypot(self.vx,self.vy,self.s)


    def update(self):
        return _e_update(self.px,self.py,self.vx,self.vy,Time.deltaTime,self.s,self.valid_particles,self.m)
        #np.hypot(self.vx,self.vy,self.s)
        #self.valid_particles[self.s < PARTICLE_SPEED_THRESHOLD] = 0
        #t = np.maximum(ONE_MINUS_FALLOFF-self.s * (self.m*Time.deltaTime) ,0.0)
        #self.vx *= t
        #self.vy *= t
        #self.px += self.vx * Time.deltaTime
        #self.py += self.vy * Time.deltaTime


class Explosion: 
    __slots__ = 'energy_per_particle','energy','hit_size','center','particles',\
    'reachable_static_entities','reachable_dynamic_entities','speed_changes'
    def __init__(self,epicenter:Vector2,energy:float):
        self.energy_per_particle = energy / PARTICLES_TO_SIMULATE
        self.energy = energy
        self.hit_size = 10 * self.energy/PARTICLES_TO_SIMULATE
        self.center = epicenter.copy()
        self.particles = ExplosionParticles(self.center,energy,1/(energy)**.5 )
        self.reachable_static_entities:list[GameObject] = []
        self.reachable_dynamic_entities:list[Moves] = []
        self.speed_changes = np.ones(PARTICLES_TO_SIMULATE,dtype=np.float32)

    def update(self):
        self.speed_changes[:] = 1.0
        any_touched = False
        for obj in self.reachable_static_entities:
            dmg = self.calculate_damage_to_entity(obj).__trunc__()
            if dmg: any_touched = dmg
        
        for obj in self.reachable_dynamic_entities:
            dmg = self.calculate_damage_to_entity(obj)
            if dmg: any_touched = dmg
            vel_mag = obj.vel.magnitude()
            if vel_mag != 0:
                # if we are moving away from explosion then do less damage, the reverse is also true
                modifier = (obj.vel/vel_mag).dot((self.center-obj.pos).normalized) * DYNAMIC_ENTITY_VELOCITY_MODIFIER * vel_mag+ 1.0 
            else:
                modifier = 1.0

            obj.take_damage((dmg*modifier).__trunc__(),EXPLOSION_DAMAGE)
        if any_touched:     
            self.particles.vx *= self.speed_changes
            self.particles.vy *= self.speed_changes
        self.particles.update()

    def calculate_damage_to_entity(self,obj:Moves|GameObject) -> float:
        p = self.particles
        dx = p.px - obj.pos.x
        dy = p.py - obj.pos.y
        return _dmg_to_ent(dx,dy,self.hit_size,self.speed_changes,self.energy_per_particle,p.valid_particles,self.energy,p.s)

    
    @property
    def isDone(self) -> bool:
        return np.max(self.particles.s) > PARTICLE_SPEED_THRESHOLD #type: ignore
class Dynamic(GameObject):
    typeid = ''
    def __init__(self,pos:Vector2,vel:Vector2):
        self.pos = pos
        self.vel = vel


if __name__ == '__main__':
    from matplotlib import pyplot
    dists = []
    iters = []
    for x in range(1,10_000,25): 
        e = Explosion(Vector2(0,0),x)
        a = 0
        while e.isDone: #type: ignore
            #print(e.particles.vx[0])
            e.update()
            a+=1
        iters.append(x)
        dists.append(e.particles.px[0])
        #print(a)
    pyplot.plot(dists)
    pyplot.plot(iters)
    pyplot.show()            
    #e.update()



if __name__ == '__main__1':
    e = ExplosionParticles(Vector2(0,0),1,1)
    updates = 0
    while np.max(e.vx) > .5: #type: ignore

        e.update()
        #print(np.max(e.vx))
        updates += 1
    print(updates)
    print(e.px[0])


