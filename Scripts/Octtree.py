from typing import Any
import glm
try:from Scripts.ChunkManager import RayTraceChunkManager
except:from ChunkManager import RayTraceChunkManager
class Octree:
    def __init__(self,position:tuple[int,int,int],size:int) -> None:
        self.root = ONode()
        self.position = glm.ivec3(position)
        self.size:int = size #represents a power of two

    def insert(self,x:int,y:int,z:int,value:Any):
        current = self.root
        ox,oy,oz = self.position

        for size in range(self.size-1,-1,-1):
            if not isinstance(current.children,list):
                current.split()
            assert isinstance(current.children,list)
            x_ = x >= ox + 2**(size)
            if x_:ox += 2**size
            y_ = y >= oy + 2**(size)
            if y_:oy += 2**size
            z_ = z >= oz + 2**(size)
            if z_:oz += 2**size
            index_to_next = int(x_) + int(y_) * 2 + int(z_) * 4
            # print('index:',index_to_next)
            if size == 0:
                current.children[index_to_next] = value
                return
                
            current = current.children[index_to_next]
            
class ONode:
    children:list['ONode']|None|Any
    def __init__(self) -> None:
        self.children = None
        
    def split(self):
        self.children = [ONode() for _ in range(8)]




def treeify(chunk_manager:RayTraceChunkManager,superchunk_position:tuple[int,int,int]):
    '''A superchunk is a 512 by 512 by 512 block region consisting of 16,777,216 normal chunks'''
    chunk_position = glm.ivec3(superchunk_position) * 64
    size = 9 #2**9 == 512
    tree = Octree(chunk_position.to_tuple(),size)
    for cx in range(chunk_position.x,chunk_position.x+64,1):
        for cy in range(chunk_position.y,chunk_position.y+64,1):
            for cz in range(chunk_position.z,chunk_position.z+64,1):
                cpos = cx,cy,cz
                if cpos not in chunk_manager.chunks: continue
                tree.insert(cx,cy,cz,chunk_manager.chunks[cpos])
    return tree
