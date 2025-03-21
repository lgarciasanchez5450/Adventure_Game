import glm
import typing
from Utils.Math.Collider import Collider

if typing.TYPE_CHECKING:
    from Scene import Scene
    
class IEntity(typing.Protocol):
    scene:'Scene'
    pos:glm.vec3
    vel:glm.vec3
    collider:Collider
    mass:float|int
    dead:bool
    forward:glm.vec3
    up:glm.vec3
    right:glm.vec3

        
    def update(self): ...

    