import typing
from Utils.Math.Collider import Collider
from Scripts.Chunk import Chunk
from Utils.Math.game_math import *
from Scripts.Entity import Entity
if typing.TYPE_CHECKING:
    from Scene import RasterScene
class Physics:
    def __init__(self,scene:"RasterScene"):
        self.blocks = []
        self.entities:list[Entity] = []
        self.scene = scene
        self.chunk_manager = scene.chunk_manager

    def addEntity(self,entity:Entity):
        self.entities.append(entity)


    def update(self):
        dt = self.scene.engine.time.dt
        all_chunks = self.chunk_manager.chunks
        entities = 0
        for chunk in map(all_chunks.__getitem__,self.chunk_manager.active_chunks):
            for entity in chunk.entities:
                entities += 1
                e_collider = entity.collider
                if entity.vel.x != 0:
                    e_collider.move_x(entity.vel.x * dt)
                    for bx,by,bz in self.getCollidingBlocks(e_collider):
                        cpos = bx//Chunk.SIZE,by//Chunk.SIZE,bz//Chunk.SIZE
                        blocks = all_chunks[cpos].blocks
                        if blocks is not None and blocks[bx%Chunk.SIZE,by%Chunk.SIZE,bz%Chunk.SIZE]:                        
                            if entity.vel.x > 0: # moving right
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
                            if entity.vel.y > 0: # moving right
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
                            if entity.vel.z > 0: # moving right
                                e_collider.setZPositive(bz)
                            else: 
                                e_collider.setZNegative(bz+1)
                            entity.vel.z = 0
                            break

                entity.vel.y -= (2.9 * 9.81)*dt  #minecraft gravity is ~2.9 times stronger than real life
                entity.vel.xz = entity.vel.xz - entity.vel.xz* 0.4
                

    def isGrounded(self,entity:Entity):
        if entity.vel.y > 0: return False
        ground_col = entity.collider.copy()
        if round(ground_col.y_negative,5).is_integer():
            ground_col.c.y -= 0.001
            for bx,by,bz in self.getCollidingBlocks(ground_col):
                cpos = bx//Chunk.SIZE,by//Chunk.SIZE,bz//Chunk.SIZE
                blocks = self.chunk_manager.chunks[cpos].blocks
                if blocks is not None and blocks[bx%Chunk.SIZE,by%Chunk.SIZE,bz%Chunk.SIZE]:                        
                    return True

    def getCollidingChunks(self,collider:Collider):
        return collide_chunks(collider.x_negative,collider.y_negative,collider.z_negative,collider.x_positive,collider.y_positive,collider.z_positive,Chunk.SIZE)
    def getCollidingBlocks(self,collider:Collider):
        return collide_chunks(collider.x_negative,collider.y_negative,collider.z_negative,collider.x_positive,collider.y_positive,collider.z_positive,1)