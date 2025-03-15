import numpy as np
class Chunk:
    '''
    Each Chunk Holds a region of 4 by 4 by 4 blocks

    Memory Layout
    Bitmask: 8 Bytes
    Blocks: 256 Bytes
    Total: 264 Bytes
    '''
    def __init__(self):
        self.bitmask = 0#0xFFFFFFFFFFFFFFFF
        self.blocks = np.zeros(shape=(4,4,4),dtype= np.uint32)

    def setVoxel(self,x:int,y:int,z:int,color:tuple[int,int,int]):
        rgb = color[0] << 16 | color[1] << 8 | color[2]
        self.blocks[x,y,z] = rgb << 8
        self.bitmask |= 1<<self.getBitmaskIndex(x,y,z)

    def removeVoxel(self,x:int,y:int,z:int):
        self.blocks[x,y,z] = 0
        
        self.bitmask = ~(~self.bitmask | 1<<self.getBitmaskIndex(x,y,z))

    def getBitmaskIndex(self,x:int,y:int,z:int):
        return x + y*4 + z * 16
    
    def empty(self):
        return not self.bitmask
    
class TreeNode:
    def __init__(self) -> None:
        self.bitmask = 0
        self.blocks = []



import moderngl as mgl

ctx = mgl.create_context()
ctx.texture((1000,2),4)




#####
#we create a texture that is n by 2 big with 4 components
# the memory layout will go like this.
# Root node
# vec4 * 8 | vec4 * 8 | 
# 



#########
#  1 Byte | 1 Byte | 1 Byte | 1 Byte
#  Red    | Green  | Blue   | misc
