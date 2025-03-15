from typing import Protocol
import glm
import numpy as np
from pygame import Surface
class Ray:
    origin:glm.vec3
    dir:glm.vec3
    dist:float
    __slots__ = 'dir','origin','dist'

class Camera(Protocol):
    position:glm.vec3
    forward:glm.vec3
    up:glm.vec3
    right:glm.vec3

def CastRay(ray:Ray,voxels:np.ndarray) -> tuple[int,int,int]:
    ray.dist = 0
    ray.dir = glm.normalize(ray.dir)
    while ray.dist < 20:
        ray.origin += ray.dir*0.1
        ray.dist += 0.1
        x,y,z = glm.ivec3(ray.origin)
        if  0<= x < voxels.shape[0] and \
            0<= y < voxels.shape[1] and \
            0<= z < voxels.shape[2]:
            


            c = voxels[x,y,z]
            if c:
                shading = 1-(ray.dist / (ray.dist+5))
                return (int((c>>24)*shading),int(shading*(c>>16 &0xFF)),int((c>>8 & 0xFF)*shading)) 
    return (39,156,226)

def CastRayDistance(ray:Ray,voxels:np.ndarray) -> float:
    ray.dist = 0
    ray.dir = glm.normalize(ray.dir)

    while ray.dist < 20:
        ray.origin += ray.dir*0.1
        ray.dist += 0.1

        x,y,z = glm.ivec3(ray.origin)
        if x < 0 or x >= voxels.shape[0] or \
            y < 0 or y >= voxels.shape[1] or \
            z < 0 or z >= voxels.shape[2]:
            break

        c = voxels[x,y,z]
        if c:
            return ray.dist
    return ray.dist
        
            
def RayTrace(camera:Camera,voxels:np.ndarray,out:Surface):
    width,height = out.get_size()
    out.lock()
    for y in range(height):
        for x in range(width):
            ray = Ray()
            ray.origin= glm.vec3(camera.position)
            horizontalCoef = 2*(x*2 - width ) / width; 
            verticalCoef   = 2*(y*2 - height) / width; 
            ray.dir = camera.forward + horizontalCoef * camera.right + verticalCoef * camera.up
            ray_color = CastRay(ray,voxels)
            # if ray.dir.y == 0:
            #     print(ray.dir,ray_color)
            out.set_at((x,height-y-1),ray_color)
    out.unlock()
