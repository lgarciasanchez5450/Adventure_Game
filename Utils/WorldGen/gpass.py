import numpy as np
CHUNK_SIZE = 8
from typing import TYPE_CHECKING
#from .utils import paste
from .types import ChunkType


class GenPass:
    def processChunk(self,chunk:ChunkType): ...



class Village(GenPass):
    chunk_size = 5 #spanning 5 chunks
    blocksize = chunk_size * CHUNK_SIZE
    generated:dict[tuple[int,int],list[list[str]]] = {}

    def processChunk(self,chunk:ChunkType):
        
        own_cx = chunk.pos[0] // self.chunk_size
        own_cy = chunk.pos[1] // self.chunk_size
        own_top = own_cy * self.chunk_size
        own_left = own_cx * self.chunk_size
        print('passing it')

        if (own_cx,own_cy) in self.generated:
            #we just figure out if any of the generation is in this chunk and update it accordingly
            pass
        else:
            make_village(own_cx,own_cy,(self.blocksize,self.blocksize))
    @staticmethod
    def addTownHall(path_connections:list[tuple[int,int]],blocks:list[list[str]],blocks_filled:np.ndarray):
        th_blocks = np.zeros((5,8)) #the town hall will be 5 by 8
        print(th_blocks)
        import random
        left_to_right = random.random() < 0.5  #determin the orientation of the townhall (village center)
        if left_to_right:
            # no need to rotate the th_blocks

            quit()



#print(paste(np.arange(16,dtype = np.int32).reshape((2,8)),np.zeros((10,10),dtype = np.int32),(5,5)))
class Structure:
    pass

town_hall = {
    'blocks': np.array([
        [1,1,1,1,1,1,1,1,1,1],
        [1,0,0,0,0,0,0,0,0,1],
        [1,0,0,0,0,0,0,0,0,1],
        [1,0,0,0,0,0,0,0,0,1],
        [1,1,1,1,2,2,1,1,1,1]
    ],np.uint32),

    'connections': np.array([ # 0 is no connection, 1 = must connect to path, 2 = path or building
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,1,1,0,0,0,0]
    ],np.uint32)
}
hut = {
    'blocks': np.array([
        [1,1,1,1,1],
        [1,0,0,0,1],
        [1,0,0,0,1],
        [1,0,0,0,1],
        [1,1,2,1,1]
    ],np.uint32),
    'connections': np.array([
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,1,0,0]
    ],np.uint32)
}
path_vert = {
    'ground': np.array([
        [1,1,1],
        [1,1,1],
        [1,1,1],
        [1,1,1],
        [1,1,1]
    ],np.uint32),
    'connections': np.array([
        [0,2,0],
        [0,0,0],
        [1,0,1],
        [0,0,0],
        [0,1,0]
    ],np.uint32)
}
path_horz = {
    'ground': np.array([
        [1,1,1,1,1],
        [1,1,1,1,1],
        [1,1,1,1,1]
    ],np.uint32),
    'connections': np.array([
        [0,0,0,0,0],
        [1,0,0,0,1],
        [0,0,0,0,0]
    ],np.uint32)
}
paths = [path_vert,path_horz]

if __name__ == '__main__':
    from utils import hash2D, randomNormalized,paste,getOnesOffset,printArray

else:
    from .utils import hash2D, randomNormalized,paste,getOnesOffset,printArray
def make_village(cx:int,cy:int, size:tuple[int,int]):
    state = np.array([hash2D(cx,cy),0],np.float32)
    filled = np.zeros(size,dtype = np.uint8)
    blocks = np.zeros(size,dtype = np.uint32)
    connections = []
    state = np.array([hash2D(cx,cy),0],dtype = np.uint32)
    village_center_pos = np.empty(2,np.int32)
    village_center_pos[0] = randomNormalized(state) * size[0]/2 + size[0]/4
    village_center_pos[1] = randomNormalized(state) * size[1]/2 + size[1]/4
    
    paste(town_hall['blocks'],blocks,village_center_pos)
    connections.extend(getOnesOffset(town_hall['connections'],village_center_pos,blocks.shape))
    printArray(blocks)
    print(connections)
    quit()



    
