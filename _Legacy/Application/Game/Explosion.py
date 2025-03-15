from typing import Iterable
from ..Utils.Math.Vector import Vector2
import numpy as np
from .Entities import GameObject
from Application.Game.Game_Typing import Moves, NotMoves
import Application.Game.Time as Time
from .Constants.DamageTypes import EXPLOSION_DAMAGE
from ..Utils.Math.Fast import njit
#PARTICLES_TO_SIMULATE = 1024
PARTICLES_TO_SIMULATE = 2_000
PARTICLE_SPEED_THRESHOLD = 10 #in units/second (not inclusive, meaining if particles are exactly at 0.5 speed then they will not be counted)
PARTICLES_THRESHOLD = 10
DYNAMIC_ENTITY_VELOCITY_MODIFIER = 0.2 # a value of 1 will completely cancel out the damage from explosion when going directly away from explosion
DEFAULT_PARTICLE_TOUCHING_DRAG = .25 #[0,1] #how much the particles will slow down when touching an object
FALLOFF = 0.0005
CONSTANT_SPEED_LOSS_AT_CRITICAL_VELOCITY = 2
# cache variables, dont change!
ONE_MINUS_FALLOFF = 1 - FALLOFF # 


@njit(boundscheck = False,cache = True)
def _dmg_to_ent(dx,dy,vx,vy, hit_size,speed_changes,energy_per_particle,valid_particles,touching_drag,s)->float:
    dists = np.hypot(dx,dy) #calc dinstance of each particle to the obj
    dists -= hit_size #subtract a margin of error due to timesteps
    np.minimum(dists,0,dists)  #get rid of all particles which arent close enough
    cond = (dx * vx + dy * vy) < 0
    hits = np.sum(np.logical_and(dists,np.logical_and(cond, valid_particles))) #count how many are colliding with obj
    if  hits < PARTICLES_THRESHOLD : return 0 #if less than 5 are colliding with us than we say that its just a stray particle and we dont count it
    #quick intermission to slow down the objects which are being collided
    dists = dists + hit_size
    dists /= hit_size

    speed_changes[cond] *= np.square(dists[cond]) * touching_drag + (1 - touching_drag) #TODO: add logic to make sure only the particles which a moving towards the entities are beingslowd down   
    #resume the normal stuff
    damage =np.sum(np.multiply(np.square(1-dists),s))* energy_per_particle * 0.1 #we need to negate the np.sum because dists are all negitve
    return damage

@njit(boundscheck = False,cache = True)
def _e_update(px,py,vx,vy,dt,s,valids,m):
    np.hypot(vx,vy,s)
    t = 1-(FALLOFF+s) * (m * dt)
    #t = np.maximum(1.0,(m*dt)*s) - 1
    #t = np.exp(-s*m*dt)
    cond = t<.2
    t[cond] = (s[cond] - CONSTANT_SPEED_LOSS_AT_CRITICAL_VELOCITY)/s[cond]
    #print(t)
    #t[t>0.5] = 0.5
    #print(t)
    #t = np.
    vx *= t
    vy *= t
    np.hypot(vx,vy,s)
    valids[s < PARTICLE_SPEED_THRESHOLD] = 0
    px += vx * dt * 0.5
    py += vy * dt * 0.5

class ExplosionParticles:
    __slots__ = 'm','px','py','vx','vy','valid_particles','s'
    def __init__(self,pos:Vector2,energy:float,m:float):
        self.m = m
        self.px = np.empty(PARTICLES_TO_SIMULATE,dtype = np.float32)
        self.py = np.empty(PARTICLES_TO_SIMULATE,dtype = np.float32)
        self.px[:] = pos.x
        self.py[:] = pos.y
        self.vx = np.cos(np.arange(PARTICLES_TO_SIMULATE,dtype = np.float32) * (6.283185307197959 / PARTICLES_TO_SIMULATE)) * (energy)
        self.vy = np.sin(np.arange(PARTICLES_TO_SIMULATE,dtype = np.float32) * (6.283185307197959 / PARTICLES_TO_SIMULATE)) * (energy)
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
    'reachable_static_entities','reachable_dynamic_entities','speed_changes','ptd',\
    'entities_damages','timer'
    def __init__(self,epicenter:Vector2,energy:float,particle_touching_drag = DEFAULT_PARTICLE_TOUCHING_DRAG):

        energy = 10 *np.log2(energy)
        assert energy > 1
        self.ptd = particle_touching_drag

        self.energy_per_particle = energy / PARTICLES_TO_SIMULATE
        self.energy = energy
        self.hit_size =1# 10 * self.energy/PARTICLES_TO_SIMULATE
        self.center = epicenter.copy()
        self.particles = ExplosionParticles(self.center,energy,1/np.sqrt(energy) )
        self.reachable_static_entities:tuple[NotMoves,...] = ()
        self.reachable_dynamic_entities:tuple[Moves,...] = ()
        self.entities_damages:list[float] = []
        self.speed_changes = np.ones(PARTICLES_TO_SIMULATE,dtype=np.float32)
        self.timer = 0.01

    def setEntities(self,static:Iterable[NotMoves],dynamic:Iterable[Moves]):
        self.reachable_dynamic_entities = tuple(dynamic)
        self.reachable_static_entities = tuple(static)

    def _removeDeads(self):
        self.reachable_dynamic_entities = tuple(filter(lambda x:not x.dead,self.reachable_dynamic_entities))
        self.reachable_static_entities = tuple(filter(lambda x:not x.dead,self.reachable_static_entities))

    def update(self):
        self.timer -= Time.deltaTime
        #print('total entities =',len(self.reachable_dynamic_entities)+len(self.reachable_static_entities))
        self.speed_changes[:] = 1.0
        any_touched = False
        for obj in self.reachable_static_entities: 
            dmg = self.calculate_damage_to_entity(obj).__trunc__() 
            if dmg: 
                any_touched = True
                obj.take_damage(dmg,EXPLOSION_DAMAGE)
         

        for entity in self.reachable_dynamic_entities:

            dmg = self.calculate_damage_to_entity(entity)
            vel_mag = entity.vel.magnitude()
            if vel_mag != 0:
                # if we are moving away from explosion then do less damage, the reverse is also true
                modifier = (entity.vel/vel_mag).dot((self.center-entity.pos).normalized) * DYNAMIC_ENTITY_VELOCITY_MODIFIER * vel_mag+ 1.0 
            else:
                modifier = 1.0
            dmg = (modifier * dmg).__trunc__()
            if dmg: 
                any_touched = True
              
                entity.take_damage(dmg,EXPLOSION_DAMAGE)
               
        if any_touched:     
            self.particles.vx *= self.speed_changes
            self.particles.vy *= self.speed_changes
            self._removeDeads()
        self.particles.update()

    def calculate_damage_to_entity(self,obj:Moves|NotMoves) -> float:
        p = self.particles
        dx = p.px - obj.pos.x
        dy = p.py - obj.pos.y
        try:
            ht = max((self.hit_size,obj.collider.get_size()/2).magnitude() * 1.5) #type: ignore
        except:
            ht = self.hit_size
        return _dmg_to_ent(dx,dy,p.vx,p.vy,ht,self.speed_changes,self.energy_per_particle,p.valid_particles,self.ptd,p.s)

    @property
    def active(self) -> bool:
        return np.any(self.particles.valid_particles) #type: ignore
    
    @property
    def isDone(self) -> bool:
        return not np.any(self.particles.valid_particles) #type: ignore
class __Dynamic(GameObject):
    typeid = ''
    def __init__(self,pos:Vector2,vel:Vector2):
        self.pos = pos
        self.vel = vel

def prediction(x:float):
    return 20* np.sqrt(10*x) - 0.71 * x
    # return 4.1 * (10 * np.log2(x)) ** 0.56


###MODULE INITIALIZATION###
e = Explosion(Vector2.zero(),10.0)
e.setEntities((__Dynamic(Vector2(100,0),Vector2.zero),),(__Dynamic(Vector2(-100,0),Vector2(1,0)),)) #type: ignore
e.update()


if __name__ == '__main__':
    '''This is code to test the stability of the explosion simulation particles along many different energy levels as well as the automatic tuning applied to each coefficient to ensure maximum stability
    It also tests how good <prediction> is at determining how far each particle could go at different energy levels. Ideally it should overshoot by a little bit to account for errors'''
    from matplotlib import pyplot
    dists = []
    #ax = pyplot.figure().add_subplot(projection='3d')

    iters = []
    start = 5
    #end = 1_000
    end = 500
    xs = []
    try:
        for x in range(start,end,1): 

            e = Explosion(Vector2(0,0),x)
            a = 0
            while e.active:
                #print(e.particles.vx[0])
                e.update()
                #print(np.sum(e.particles.valid_particles))
                #ax.plot(e.particles.px,e.particles.py,zs= [a] * PARTICLES_TO_SIMULATE)
                a+=1
            print(f"{100*(x-start+1)/(end-start):.2f}%",end= '\r')
            xs.append(x)
            dists.append(e.particles.px[0])
            #print(x,a)
            #iters.append(x)
    except:
        print('energy too low')
    #print(a)
    pyplot.plot(xs,prediction(np.array(xs)),color='green') #type: ignore

    pyplot.plot(xs,dists)
    pyplot.show()    

        
    #e.update()



