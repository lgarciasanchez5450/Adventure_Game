import typing
import pygame
import numpy as np
import glm
from Scripts import Biome
from Scripts import Ground
import moderngl as mgl
if typing.TYPE_CHECKING:
    from Scripts.Block import Block
    from Scripts.Entity import Entity

class ChunkStatus:
    JUST_CREATED = 0
    GENERATED = 1
    SERIALIZING = 2
    DESERIALIZING = 3
    GENERATING = 4



class Chunk:
    SIZE = 32
    __slots__ = 'status','pos','blocks','biome','dimension','entities'
    def __init__(self,pos:tuple[int,int,int]) -> None:
        self.status = ChunkStatus.JUST_CREATED
        self.pos = pos
        self.blocks:typing.Optional[np.ndarray] = None #np.empty((Chunk.SIZE,Chunk.SIZE,Chunk.SIZE),dtype=np.uint16)
        self.biome = np.empty((Chunk.SIZE//2,Chunk.SIZE//2,Chunk.SIZE//2),dtype=np.uint8)
        self.dimension:int|float # which dimension is this chunk primarily? [1,2] -> [overworld,nether]


        self.entities:list['Entity'] = []

    
    def addEntity(self,entity:"Entity"):
        self.entities.append(entity)

    def update(self,moved_to:list[tuple['Entity',tuple[int,int,int]]]):

        for i in range(len(self.entities)-1,-1,-1):
            entity = self.entities[i]
            entity.update()
            if (cpos := glm.ivec3(entity.pos//Chunk.SIZE).to_tuple()) != self.pos:
                moved_to.append((entity,cpos))
                self.entities.pop(i)

