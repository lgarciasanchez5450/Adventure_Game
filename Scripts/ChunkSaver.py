import typing
from Utils.Async.AsyncManager import AsyncManager,read_async
from Scripts.Chunk import Chunk 
from zlib import compress, decompress
import os

def read_and_decompress(path:str):
    with open(path,'rb') as file:
        b = file.read()
    yield 
    return decompress(b)

class ChunkSaver:
    __slots__ = 'dirpath','queued','chunks_saved','read_async_manager'
    def __init__(self,dirpath:str):
        self.dirpath = dirpath
        # os.makedirs(self.dirpath,exist_ok=True)
        self.queued:list[Chunk] = [] #type: ignore
        self.chunks_saved:dict[tuple[int,int,int],int] = {}
        self.read_async_manager = AsyncManager()

    def update(self):      
        for i in range(5):
            if not self.read_async_manager.is_done():
                self.read_async_manager.update_loop()
            else: break
        for i in range(3):
            if not self.queued: break
            chunk = self.queued[-1]
            if chunk.status == ChunkStatus.GENERATED:
                self.queued.pop()
                filename = f'{chunk.pos[0]}l{chunk.pos[1]}l{chunk.pos[2]}'
                self.chunks_saved[chunk.pos] = -1
                with open(os.path.join(self.dirpath,filename),'wb+') as file:
                    file.write(compress(serialize(chunk))) 
                    
            
    def savechunk(self,chunk:Chunk): 
        self.chunks_saved[chunk.pos] = len(self.queued)
        self.queued.append(chunk)

    def getchunk(self,cpos:tuple[int,int,int]) -> Chunk: 
        index = self.chunks_saved[cpos]
        if index != -1:
            chunk = self.queued[index]
            if chunk is not None:
                return chunk
        filename = 'l'.join(map(str,cpos))
        with open(os.path.join(self.dirpath,filename),'rb') as file:
            return deserialize((file.read()),cpos)
            
    def getchunkasync(self,cpos:tuple[int,int,int]) -> Chunk:
        index = self.chunks_saved[cpos]
        if index != -1:
            return self.queued[index] #type: ignore
        else:
            filename = 'l'.join(map(str,cpos))
            c = Chunk(cpos)
            self.read_async_manager.submit_async(read_and_decompress(os.path.join(self.dirpath,filename)),lambda bytes: deserialize(bytes,cpos,c))
            return c
        
    def haschunk(self,cpos:tuple[int,int,int]):
        return cpos in self.chunks_saved


def serialize(chunk:Chunk) -> bytes:
    dimension = chunk.dimension
    b_blocks = b'' if chunk.blocks is None else chunk.blocks.tobytes('C') 
    b_biomes = chunk.biome.tobytes('C')   
    return str(dimension).encode() + b';' +(len(b_blocks)).to_bytes(4)+b_blocks+(len(b_biomes)).to_bytes(4)+b_biomes

from Scripts.Chunk import ChunkStatus
def deserialize(b:bytes,pos:tuple[int,int,int],chunk:typing.Optional[Chunk] = None) -> Chunk:
    i = b.find(b';')
    assert i != -1
    dim = float(b[:i].decode())
    b = b[i+1:]
    len_blocks = int.from_bytes(b[:4])
    blocks = b[4:len_blocks+4]
    b = b[len_blocks+4:]
    len_biomes = int.from_bytes(b[:4])
    biomes = b[4:len_biomes+4]
    import numpy as np
    if chunk is None:
        chunk = Chunk(pos)
    chunk.status = ChunkStatus.GENERATED
    if blocks == b'':
        chunk.blocks = None
    else:
        chunk.blocks = np.empty((Chunk.SIZE,Chunk.SIZE,Chunk.SIZE),np.uint16)
        chunk.blocks[:] = np.frombuffer(blocks,dtype=np.uint16).reshape((Chunk.SIZE,Chunk.SIZE,Chunk.SIZE))
    chunk.biome[:] = np.frombuffer(biomes,dtype=np.uint8).reshape((Chunk.SIZE//2,Chunk.SIZE//2,Chunk.SIZE//2))
    chunk.dimension = dim
    return chunk