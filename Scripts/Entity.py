import typing
import glm
from Utils.Math.Collider import Collider
if typing.TYPE_CHECKING:
    from Scene import RasterScene
class Entity:
    __slots__ = 'scene','pos','vel','collider','mass','dead','dir'
    def __init__(self,scene:'RasterScene',position:tuple[int,int,int],size:tuple[float,float,float]|glm.vec3) -> None:
        self.scene = scene
        self.pos = glm.vec3(position)
        self.vel = glm.vec3(0,0,0)
        self.collider = Collider(self.pos,size)
        self.mass = 1 #kg
        self.dead = False
        
    def update(self): ...

    