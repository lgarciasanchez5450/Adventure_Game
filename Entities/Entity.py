import glm
import typing
from Utils.Math.Collider import Collider

if typing.TYPE_CHECKING:
    from Scene import Scene
    
class Entity:
    __slots__ = 'scene','pos','vel','collider','mass','dead','dir','forward','up','right'
    def __init__(self,scene:'Scene',position:tuple[int,int,int],size:tuple[float,float,float]|glm.vec3) -> None:
        self.scene = scene
        self.pos = glm.vec3(position)
        self.vel = glm.vec3(0,0,0)
        self.collider = Collider(self.pos,size)
        self.mass = 1.0 #kg
        self.dead = False #this <dead> flag is ONLY to signal to the scene that it should be deleted soon

        self.forward = glm.vec3(1,0,0)
        self.up = glm.vec3(0,1,0)
        self.right = glm.vec3(0,0,1)
        
    def update(self): ...

    