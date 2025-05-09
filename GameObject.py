import glm
from gametypes import *
from Utils.Math.Collider import Collider

class GameObject:
    __slots__ = 'name','pos','vel','collider','mass','dead','dir','forward','up','right','behaviours'
    def __init__(self,name:str,pos:tuple[int,int,int]|glm.vec3,vel:glm.vec3,mass:float,size:tuple[float,float,float]|glm.vec3,behaviours:list[BehaviourType]):
        self.name = name
        self.mass = mass
        self.pos = glm.vec3(pos)
        self.vel = vel
        self.collider = Collider(self.pos,size)
        self.dead = False #this <dead> flag is ONLY to signal to the scene that it should be deleted soon
        self.behaviours = behaviours

        # self.forward = glm.vec3(1,0,0)
        # self.up = glm.vec3(0,1,0)
        # self.right = glm.vec3(0,0,1)
        
    def update(self,engine:EngineType):
        for b in self.behaviours:
            b.update(self,engine)

    