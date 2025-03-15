# from Scripts.Chunk import Chunk
import moderngl as mgl
import numpy as np
import typing
from Scripts.Chunk import Chunk,ChunkStatus
import glm
from Utils.Math.Fast import njit,literal_unroll
if typing.TYPE_CHECKING:
    from Scene import RasterScene

class ChunkMesh:
    __slots__ = 'ctx','model_uniform','program','vao','vbo','dirty','chunk','lod'
    def __init__(self,ctx:mgl.Context,program:mgl.Program,chunk:Chunk) -> None:
        
        self.ctx = ctx
        self.model_uniform = program['m_model']
        self.program = program
        self.vao = None
        self.vbo = None
        self.chunk = chunk
        self.lod = 1 #1 -> full scale, 

    def setLOD(self,newLOD:int):
        self.lod = newLOD
        
    def buildMesh(self):
        if self.chunk.status != ChunkStatus.GENERATED: return False
        if self.chunk.blocks is None: return True
        if not np.any(self.chunk.blocks): 
            return True
        if self.vbo is not None: self.vbo.release()
        if self.vao is not None: self.vao.release()
        mesh = build_mesh(self.chunk.blocks,self.lod)
        if mesh.size == 0: 
            self.vao = None
            self.vbo = None
            return True
        self.vbo = self.ctx.buffer(mesh)
        assert isinstance(self.vbo,mgl.Buffer),f'Mesh Len: {mesh.size}. Mesh: {mesh}'
        self.vao = self.ctx.vertex_array(self.program,[(self.vbo,'3i i i','in_position','in_face','in_block_id')])
        assert isinstance(self.vao,mgl.VertexArray),f'VBO:{self.vbo}'
        return True

    def render(self):
        if self.vao is None: return
        self.model_uniform.write(glm.translate(glm.vec3(self.chunk.pos) * Chunk.SIZE)) #type: ignore
        self.vao.render()
        

    def release(self):
        if self.vao is not None:
            self.vao.release()
            self.vao = None
        if self.vbo is not None:
            self.vbo.release()
            self.vao = None

        del self.model_uniform
        del self.chunk
        del self.ctx
        del self.program

def build_mesh(b:np.ndarray,lod:int):
    if lod==1:
        return _build_mesh(b,Chunk.SIZE)   
    elif (Chunk.SIZE/lod).is_integer():  # or Chunk.Size%lod == 0
        return _build_mesh_low_detail(b,Chunk.SIZE,lod)
    else:
        raise RuntimeError


@njit(boundscheck=False,cache=True)
def add_data(vertex_data, index, *verticies):
    for vertex in literal_unroll(verticies):
        vertex_data[index] = vertex
        index += 1
    return index

@njit(cache=True)
def _build_mesh(b:np.ndarray,chunk_size):
    # array wil hold [vertex(x,y,z), face_id,block_id]
    data = np.empty((chunk_size**3 * 4*6*6),np.uint32)
    index = 0

    def is_air(b:np.ndarray,x,y,z):
        if x < 0 or y < 0 or z < 0: return True
        s = b.shape[0]
        if x >= s or y >= s or z >= s: return True
        return b[x,y,z] == 0
    
    for x in range(chunk_size):
        for y in range(chunk_size):
            for z in range(chunk_size):
                if b[x,y,z] == 0: continue
                block_id  = b[x,y,z]
                #top
                if is_air(b,x,y+1,z):
                    index = add_data(data,index,
                                    x,y+1,z,0,block_id,
                                    x,y+1,z+1,0,block_id,
                                    x+1,y+1,z+1,0,block_id,
                                    x,y+1,z,0,block_id,
                                    x+1,y+1,z+1,0,block_id,
                                    x+1,y+1,z,0,block_id,
                                    )
                #bottom
                if is_air(b,x,y-1,z):
                    index = add_data(data,index,
                                    x,y,z,1,block_id,
                                    x+1,y,z+1,1,block_id,
                                    x,y,z+1,1,block_id,
                                    x,y,z,1,block_id,
                                    x+1,y,z,1,block_id,
                                    x+1,y,z+1,1,block_id,
                                    )
                #x+
                if is_air(b,x+1,y,z):
                    index = add_data(data,index,
                                    x+1,y+1,z+1,2,block_id,
                                    x+1,y,z+1,2,block_id,
                                    x+1,y,z,2,block_id,
                                    x+1,y+1,z+1,2,block_id,
                                    x+1,y,z,2,block_id,
                                    x+1,y+1,z,2,block_id,
                                )
                #x-
                if is_air(b,x-1,y,z):
                    index = add_data(data,index,
                                    x,y+1,z,3,block_id,
                                    x,y,z,3,block_id,
                                    x,y,z+1,3,block_id,
                                    x,y+1,z,3,block_id,
                                    x,y,z+1,3,block_id,
                                    x,y+1,z+1,3,block_id,
                                )
                #z+
                if is_air(b,x,y,z+1):
                    index = add_data(data,index,
                                    x,y+1,z+1,4,block_id,
                                    x,y,z+1,4,block_id,
                                    x+1,y,z+1,4,block_id,
                                    x,y+1,z+1,4,block_id,
                                    x+1,y,z+1,4,block_id,
                                    x+1,y+1,z+1,4,block_id,
                                )
                #z-
                if is_air(b,x,y,z-1):
                    index = add_data(data,index,
                                    x+1,y+1,z,5,block_id,
                                    x+1,y,z,5,block_id,
                                    x,y,z,5,block_id,
                                    x+1,y+1,z,5,block_id,
                                    x,y,z,5,block_id,
                                    x,y+1,z,5,block_id,
                                )

    return data[:index]
 

@njit
def _build_mesh_low_detail(b:np.ndarray,chunk_size,skip:int):
    
    # array wil hold [vertex(x,y,z), face]
    data = np.empty((((chunk_size//skip)+1)**3 * 4*6*6),np.uint32)
    index = 0

    def is_air(b:np.ndarray,x,y,z):
        if x < 0 or y < 0 or z < 0: return True
        s = b.shape[0]
        if x >= s or y >= s or z >= s: return True
        return b[x,y,z] == 0
    
    for x in range(0,chunk_size,skip):
        for y in range(0,chunk_size,skip):
            for z in range(0,chunk_size,skip):
                if b[x,y,z] == 0: continue
                b_id  = b[x,y,z]
                #top
                if is_air(b,x,y+skip,z):
                    index = add_data(data,index,
                                    x,y+skip,z,0,b_id,
                                    x,y+skip,z+skip,0,b_id,
                                    x+skip,y+skip,z+skip,0,b_id,
                                    x,y+skip,z,0,b_id,
                                    x+skip,y+skip,z+skip,0,b_id,
                                    x+skip,y+skip,z,0,b_id,
                                    )

                #bottom
                if is_air(b,x,y-skip,z):
                    index = add_data(data,index,
                                    x,y,z,1,b_id,
                                    x+skip,y,z+skip,1,b_id,
                                    x,y,z+skip,1,b_id,
                                    x,y,z,1,b_id,
                                    x+skip,y,z,1,b_id,
                                    x+skip,y,z+skip,1,b_id,
                                    )
                #x+
                if is_air(b,x+skip,y,z):
                    index = add_data(data,index,
                                    x+skip,y+skip,z+skip,2,b_id,
                                    x+skip,y,z+skip,2,b_id,
                                    x+skip,y,z,2,b_id,
                                    x+skip,y+skip,z+skip,2,b_id,
                                    x+skip,y,z,2,b_id,
                                    x+skip,y+skip,z,2,b_id,
                                )
                #x-
                if is_air(b,x-skip,y,z):
                    index = add_data(data,index,
                                    x,y+skip,z+skip,3,b_id,
                                    x,y,z,3,b_id,
                                    x,y,z+skip,3,b_id,
                                    x,y+skip,z+skip,3,b_id,
                                    x,y+skip,z,3,b_id,
                                    x,y,z,3,b_id,
                                )
                #z+
                if is_air(b,x,y,z+skip):
                    index = add_data(data,index,
                                    x,y+skip,z+skip,4,b_id,
                                    x,y,z+skip,4,b_id,
                                    x+skip,y,z+skip,4,b_id,
                                    x,y+skip,z+skip,4,b_id,
                                    x+skip,y,z+skip,4,b_id,
                                    x+skip,y+skip,z+skip,4,b_id,
                                )
                #z-
                if is_air(b,x,y,z-skip):
                    index = add_data(data,index,
                                    x+skip,y+skip,z,4,b_id,
                                    x+skip,y,z,4,b_id,
                                    x,y,z,4,b_id,
                                    x+skip,y+skip,z,4,b_id,
                                    x,y,z,4,b_id,
                                    x,y+skip,z,4,b_id,
                                )

    return data[:index]