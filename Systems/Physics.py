import typing
import glm
from Utils.Math.Collider import Collider
from Scripts.Chunk import Chunk
from Utils.Math.game_math import *
from Entities.Entity import Entity
if typing.TYPE_CHECKING:
    from Scene import Scene
class Physics:
    def __init__(self,scene:"Scene"):
        self.entities:list[Entity] = []
        self.scene = scene
        self.chunk_manager = scene.s_chunk_manager

    def addEntity(self,entity:Entity):
        self.entities.append(entity)

    def update(self):
        dt = self.scene.engine.time.dt
        if dt > 0.05: 
            print('DT:',dt)
            dt = 0.05

        all_chunks = self.chunk_manager.chunks
        for entity in self.scene.entities:
            #Apply Early Forces
            entity.vel.y -= (2.9 * 9.81)*dt  #minecraft gravity is ~2.9 times stronger than real life
            e_collider = entity.collider
            if entity.vel.x != 0:
                e_collider.move_x(entity.vel.x * dt)
                for bx,by,bz in self.getCollidingBlocks(e_collider):
                    cpos = bx//Chunk.SIZE,by//Chunk.SIZE,bz//Chunk.SIZE
                    blocks = all_chunks[cpos].blocks
                    if blocks is not None and blocks[bx%Chunk.SIZE,by%Chunk.SIZE,bz%Chunk.SIZE]:                        
                        if entity.vel.x > 0:
                            e_collider.setXPositive(bx)
                        else: 
                            e_collider.setXNegative(bx+1)
                        entity.vel.x = 0
                        break
            if entity.vel.y != 0:
                e_collider.move_y(entity.vel.y * dt)
                for bx,by,bz in self.getCollidingBlocks(e_collider):
                    cpos = bx//Chunk.SIZE,by//Chunk.SIZE,bz//Chunk.SIZE
                    blocks = all_chunks[cpos].blocks
                    if blocks is not None and blocks[bx%Chunk.SIZE,by%Chunk.SIZE,bz%Chunk.SIZE]:                        
                        if entity.vel.y > 0: 
                            e_collider.setYPositive(by)
                        else: 
                            e_collider.setYNegative(by+1)
                        entity.vel.y = 0
                        break
            if entity.vel.z != 0:
                e_collider.move_z(entity.vel.z * dt)
                for bx,by,bz in self.getCollidingBlocks(e_collider):
                    cpos = bx//Chunk.SIZE,by//Chunk.SIZE,bz//Chunk.SIZE
                    blocks = all_chunks[cpos].blocks
                    if blocks is not None and blocks[bx%Chunk.SIZE,by%Chunk.SIZE,bz%Chunk.SIZE]:                        
                        if entity.vel.z > 0: 
                            e_collider.setZPositive(bz)
                        else: 
                            e_collider.setZNegative(bz+1)
                        entity.vel.z = 0
                        break
            #Apply Friction
            entity.vel.xz = entity.vel.xz - entity.vel.xz* 10 * dt

    # def isGrounded(self,entity:Entity):
    #     if entity.vel.y > 0: return False
    #     ground_col = entity.collider.copy()
    #     if round(ground_col.y_negative,5).is_integer():
    #         ground_col.c.y -= 0.001
    #         for bx,by,bz in self.getCollidingBlocks(ground_col):
    #             cpos = bx//Chunk.SIZE,by//Chunk.SIZE,bz//Chunk.SIZE
    #             blocks = self.chunk_manager.chunks[cpos].blocks
    #             if blocks is not None and blocks[bx%Chunk.SIZE,by%Chunk.SIZE,bz%Chunk.SIZE]:                        
    #                 return True

    def RayCast(self,pos:glm.vec3,dir:glm.vec3,r:float) -> tuple[float,glm.ivec3,glm.ivec3]|None:
        '''Returns Distance Traveled and Block Position'''
        
        chunks = self.chunk_manager.chunks

        MAX_RAD_SQR = r*r
        mapX = floor(pos.x)
        mapY = floor(pos.y)
        mapZ = floor(pos.z)
        deltaDistX = float('inf') if dir.x == 0 else abs(1/dir.x)
        deltaDistY = float('inf') if dir.y == 0 else abs(1/dir.y)
        deltaDistZ = float('inf') if dir.z == 0 else abs(1/dir.z)
        if (dir.x < 0):
            stepX = -1
            sideDistX = (pos.x - mapX) * deltaDistX
        else:
            stepX = 1
            sideDistX = (mapX + 1.0 - pos.x) * deltaDistX
        if (dir.y < 0):
            stepY = -1
            sideDistY = (pos.y - mapY) * deltaDistY
        else:
            stepY = 1
            sideDistY = (mapY + 1.0 - pos.y) * deltaDistY
        if (dir.z < 0):
            stepZ = -1
            sideDistZ = (pos.z - mapZ) * deltaDistZ
        else:
            stepZ = 1
            sideDistZ = (mapZ + 1.0 - pos.z) * deltaDistZ
        while True:
            m = min(sideDistX,sideDistY,sideDistZ)
            if (sideDistX == m):
                sideDistX += deltaDistX
                mapX += stepX
                side=0
            elif (sideDistY == m):
                sideDistY += deltaDistY
                mapY += stepY
                side=1
            elif sideDistZ == m:
                sideDistZ += deltaDistZ
                mapZ += stepZ
                side=2
            
            #Check if ray hit block
            distanceSqr = distanceToBoxSqr(pos,glm.vec3(mapX,mapY,mapZ))
            if distanceSqr > MAX_RAD_SQR: return
            #Check if outside the world
            cpos = mapX//Chunk.SIZE,mapY//Chunk.SIZE,mapZ//Chunk.SIZE
            if (chunk := chunks.get(cpos)):
                if chunk.blocks is not None and chunk.blocks[mapX%Chunk.SIZE,mapY%Chunk.SIZE,mapZ%Chunk.SIZE] != 0:
                    posi = glm.ivec3(mapX,mapY,mapZ)
                    adj = glm.ivec3(0,0,0)
                    adj[side] = -glm.ivec3(stepX,stepY,stepZ)[side]
                    adj += posi
                    return sqrt(distanceSqr),adj,posi
    
    def getCollidingChunks(self,collider:Collider):
        return collide_chunks(collider.x_negative,collider.y_negative,collider.z_negative,collider.x_positive,collider.y_positive,collider.z_positive,Chunk.SIZE)
  
    def getCollidingBlocks(self,collider:Collider):
        return collide_chunks(collider.x_negative,collider.y_negative,collider.z_negative,collider.x_positive,collider.y_positive,collider.z_positive,1)
    
def distanceToBoxSqr(point:glm.vec3,box:glm.vec3):
    q = glm.abs(point-box-glm.vec3(0.5)) - glm.vec3(0.5)
    return glm.dot(q,q)
