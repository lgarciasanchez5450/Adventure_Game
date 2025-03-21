import typing
import numpy as np

class ChunkStatus:
    JUST_CREATED = 0
    GENERATED = 1
    SERIALIZING = 2
    DESERIALIZING = 3
    GENERATING = 4


class Chunk:
    SIZE = 32
    __slots__ = 'status','pos','blocks','biome','dimension'
    def __init__(self,pos:tuple[int,int,int]) -> None:
        self.status = ChunkStatus.JUST_CREATED
        self.pos = pos
        self.blocks:typing.Optional[np.ndarray] = None #np.empty((Chunk.SIZE,Chunk.SIZE,Chunk.SIZE),dtype=np.uint16)
        self.biome = np.empty((Chunk.SIZE//2,Chunk.SIZE//2,Chunk.SIZE//2),dtype=np.uint8)
        self.dimension:int|float # which dimension is this chunk primarily? [1,2] -> [overworld,nether]
    
