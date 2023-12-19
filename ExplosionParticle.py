from game_math import Vector2
import Time
class ExplosionParticle: #THIS SHOULDN'T INHERIT FROM GAMEOBJECT TO SQUEEZE EVERY POSSIBLE NANOSECOND OF PERFORMANCE AND MEMORY 
    __slots__= 'x','y','vx','vy','j'
    def __init__(self,pos:Vector2, vel: Vector2, energy: float):
        self.x = pos.x
        self.y = pos.y
        self.vx = vel.x
        self.vy = vel.y
        self.j = energy

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.j *= .8
        self.j -= 1

import numpy as np
from debug import profile
#PARTICLES_TO_SIMULATE = 1024
PARTICLES_TO_SIMULATE = 2_000
PARTICLES_K_FRICTION = 0.35
PARTICLES_CROSS_SECTIONAL_AREA = 1
FALLOFF = 0.01
m = 1

Time.deltaTime = 1/60
class ExplosionParticles:
    @profile
    def __init__(self,pos:Vector2,energy:float = 1):
        self.px = np.empty(PARTICLES_TO_SIMULATE,dtype = np.float32)
        self.py = np.empty(PARTICLES_TO_SIMULATE,dtype = np.float32)
        self.px[:] = pos.x
        self.py[:] = pos.y
        self.vx = np.cos(np.arange(PARTICLES_TO_SIMULATE,dtype = np.float32) * (6.283185307197959 / PARTICLES_TO_SIMULATE)) * energy
        self.vy = np.sin(np.arange(PARTICLES_TO_SIMULATE,dtype = np.float32) * (6.283185307197959 / PARTICLES_TO_SIMULATE)) * energy

        #print(self.px, self.px.dtype)
    def update(self):
        self.px += self.vx * Time.deltaTime
        self.py += self.vy * Time.deltaTime
        v = np.hypot(self.vx,self.vy)
        t = np.maximum(1-m*v * Time.deltaTime - FALLOFF,0.0)
        self.vx *= t
        self.vy *= t




e = ExplosionParticles(Vector2(0,0),1)
updates = 0
while np.max(e.vx) > .5: #type: ignore

    e.update()
    #print(np.max(e.vx))
    updates += 1
print(updates)
print(e.px[0])


