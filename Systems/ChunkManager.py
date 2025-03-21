import typing
import glm

if typing.TYPE_CHECKING:
    from Scene import Scene
from time import perf_counter
from Utils.debug import profile
from Utils.Pipeline import Pipeline
from collections import deque

from Scripts.Chunk import Chunk
from Scripts.ChunkMesh import ChunkMesh
from Scripts.ChunkSaver import ChunkSaver
from Scripts.TerrainGeneration import TerrainNode,StructureNode

RENDER_DISTANCE = 5
SIMULATION_DISTANCE = 1
LOD_1 = 7
LOD_2 = 11
class ChunkManager:
    def __init__(self,scene:"Scene") -> None:
        self.scene = scene
        self.chunk_saver = ChunkSaver('Temp')
        self.ctx = scene.ctx

        self.chunks:dict[tuple[int,int,int],Chunk] = {}
        self.active_chunks:set[tuple[int,int,int]] = set()
        self.chunkmeshes:dict[tuple[int,int,int],ChunkMesh] = {}
        self.render_chunks:set[tuple[int,int,int]] = set()
        self.out:deque[Chunk] = deque()
        structure_node = StructureNode(self.out)
        terrain_node = TerrainNode(structure_node.queued)
        self.worldgen_pipeline = Pipeline([terrain_node],[],[structure_node])
        
        self.dirty_chunks:set[tuple[int,int,int]] = set()
        self.to_offload = set()

    def update(self):
        for _ in range(10):
            if not self.dirty_chunks: break
            cpos = self.dirty_chunks.pop()
            if self.chunkmeshes[cpos].buildMesh() is False:
                self.dirty_chunks.add(cpos) #mesh build failed
        for _ in range(20):
            self.worldgen_pipeline.update()
        for out in self.out:
            self.dirty_chunks.add(out.pos)
        self.out.clear()
        # self.chunk_saver.update()

        # if self.to_offload:
        #     try:
        #         for _ in range(20):
        #             cpos = self.to_offload.pop()
        #             self.chunk_saver.savechunk(self.chunks.pop(cpos))
        #             self.chunkmeshes.pop(cpos).release()
        #     except KeyError:
        #         pass
        # if len(self.chunks) > RENDER_DISTANCE*RENDER_DISTANCE*7:
        #     over = len(self.chunks) - RENDER_DISTANCE*RENDER_DISTANCE*7
        #     cam_pos = self.scene.camera.last
        #     s = sorted(self.chunks.keys(),key=lambda x: glm.distance2(cam_pos,x))
        #     self.to_offload.update(s[-over:])
        #     self.to_offload.difference_update(self.active_chunks)

    def draw(self):
        for cpos in self.render_chunks:
            self.chunkmeshes[cpos].render()

    def getChunk(self,cpos:tuple[int,int,int]):
        if (c:= self.chunks.get(cpos)) is not None: return c
        elif self.chunk_saver.haschunk(cpos):
            chunk = self.chunk_saver.getchunkasync(cpos)
            self.chunkmeshes[cpos] = ChunkMesh(self.scene.ctx,self.scene.program,chunk)
            self.chunks[cpos] = chunk
            return chunk
        c = self.chunks[cpos] = Chunk(cpos)
        self.worldgen_pipeline.queueChunk(c)
        self.chunkmeshes[cpos] = ChunkMesh(self.ctx,self.scene.program,c)
        return c

    def unloadChunk(self,cpos:tuple[int,int,int]):
        return self.unloadChunks({cpos})
        chunk = self.getChunk(cpos)
        if chunk.pos not in self.active_chunks: return
        self.active_chunks.remove(chunk.pos)

    def unloadChunks(self,chunks:set[tuple[int,int,int]]):
        self.render_chunks.difference_update(chunks)

    def loadChunk(self,cpos:tuple[int,int,int]):
        return self.loadChunks({cpos})
   
    def loadChunks(self,chunks:set[tuple[int,int,int]]):
        new_chunks = chunks.difference(self.render_chunks)
        for cpos in new_chunks:
            if cpos not in self.chunks:
                if self.chunk_saver.haschunk(cpos):
                    c = self.chunk_saver.getchunkasync(cpos)
                else:
                    c = Chunk(cpos)
                    self.worldgen_pipeline.queueChunk(c)
                    self.chunks[cpos] = c
                self.chunkmeshes[cpos] = ChunkMesh(self.ctx,self.scene.program,c)
        self.render_chunks.update(new_chunks)
    
    def recalculateActiveChunks(self,cx,cy,cz):
        #get chunks that will be added
        new_render = getAroundRenderDistance(cx,cy,cz)
        # lod_2 = getAroundLOD(cx,cy,cz,LOD_2)
        # lod_2.difference_update(full)
        self.unloadChunks(self.render_chunks)
        self.loadChunks(new_render)
        # for cpos in new_render:
        #     if cpos in self.chunkmeshes:
        #         cm = self.chunkmeshes[cpos]
        #         cm.lod = 1
        #         self.dirty_chunks.add(cpos)
        
        self.active_chunks =  getAroundSimulationDistance(cx,cy,cz)

        #get chunks that will be removed
        # removed_chunks = self.active_chunks.difference(new_chunks)

        # new_renders = new_render.difference(self.render_chunks)
        # for cpos in new_renders:
        #     if cpos not in self.chunks:
        #         if self.chunk_saver.haschunk(cpos):
        #             c = self.chunk_saver.getchunkasync(cpos)
        #         else:
        #             c = Chunk(cpos)
        #             self.terrain_gen.queueChunk(c)
        #         self.chunks[cpos] = c
        #         cm = self.chunkmeshes[cpos] = ChunkMesh(self.ctx,self.scene.program,c)

        # self.render_chunks = new_render

    def placeBlock(self,block:glm.ivec3,block_id:int):
        cpos = block//Chunk.SIZE
        c = self.chunks.get(cpos.to_tuple())
        if c is None: return False
        blocks = c.blocks
        if blocks is None: return False
        block = block%Chunk.SIZE
        blocks[block.x,block.y,block.z] = block_id
        self.dirty_chunks.add(cpos.to_tuple())
        return True



# def chunk():
#     return np.zeros((4,4,4),dtype=np.uint32)


# RECLAIM_CHUNKS = True
# class RayTraceChunkManager:
    
#     def __init__(self):
#         self.chunks:dict[tuple[int,int,int],np.ndarray] = {}

#     def setVoxel(self,x:int,y:int,z:int,value:int):
#         cpos = (x//4,y//4,z//4)
#         if cpos not in self.chunks:
#             self.chunks[cpos] = chunk()
#         self.chunks[cpos][x%4,y%4,z%4] = value
    
#     def getVoxel(self,x:int,y:int,z:int,value:int):
#         cpos = (x//4,y//4,z//4)
#         if cpos in self.chunks:
#             return self.chunks[x%4,y%4,z%4]
#         return None
    
#     def removeVoxel(self,x:int,y:int,z:int):
#         cpos = (x//4,y//4,z//4)
#         chunk = self.chunks.get(cpos)
#         if chunk is not None:
#             chunk[x%4,y%4,z%4] = 0
#             if RECLAIM_CHUNKS and not np.any(chunk):
#                 del self.chunks[cpos]

    # def texturize(self):
    #     from Scripts import Octtree

    #     tree = Octtree.treeify(self,(0,0,0))
    #     arr = np.empty((100_000*2),dtype=np.uint32)
    #     index = 0
    #     def fill(node:Octtree.ONode,layer:int=0):
    #         nonlocal index
    #         if node.children is None: return False
    #         if layer == 8:
    #             chunk:Chunk = 
                
    #         current_index = index
    #         index += 8 #reserve the space for this chunk
    #         for i in range(8):
    #             if fill(node.children,layer+1)



from Utils.Math.Fast import cache
# def getAround(x:int,y:int,z:int):
#     xzr = 16
#     yr = 5
#     return [(dx+x,dy+y,dz+z) for dx,dy,dz in  getDeltas(xzr,yr)]
  
def getAroundRenderDistance(x:int,y:int,z:int):
    return {(dx+x,dy+y,dz+z) for dx,dy,dz in getDeltas(RENDER_DISTANCE,RENDER_DISTANCE)}

def getAroundLOD(x:int,y:int,z:int,LOD:int):
    return {(dx+x,dy+y,dz+z) for dx,dy,dz in getDeltas(LOD,5)}


def getAroundSimulationDistance(x:int,y:int,z:int):
    return {(dx+x,dy+y,dz+z) for dx,dy,dz in getDeltas(SIMULATION_DISTANCE,SIMULATION_DISTANCE)}
@cache
def getDeltas(xzr:int,yr:int):
    deltas:list[tuple[int,int,int]] = []
    sqr_xzr = xzr*xzr-0.1 # remove the annoying nub
    for dx in range(-xzr,xzr+1,1):
        for dy in range(-yr,yr+1,1):
            for dz in range(-xzr,xzr+1,1):
                if dx*dx+dz*dz <= sqr_xzr:
                    deltas.append((dx,dy,dz)) 
    return deltas
