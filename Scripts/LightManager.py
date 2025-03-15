import typing
import numpy as np
from numpy import typing as np_typing
from Utils.Math.game_math import *
from Chunk import Chunk
if typing.TYPE_CHECKING:
    from Scripts.ChunkManager import ChunkManager
class LightManager:
    def __init__(self,chunkmanager:"ChunkManager"):
        self.chunkmanager = chunkmanager
        self.global_light = 0
        self.dirty_chunks = set()
        self.light_chunks:dict[tuple[int,int],list[tuple[int,int,int]]] = {}
        self.flooded_light_chunks:dict[tuple[int,int],np_typing.NDArray[np.uint8]] = {}

    def addLightSource(self,position:tuple[int,int],brightness:int):
        assert brightness < 256
        
        cx = position[0]//Chunk.SIZE
        cy = position[1]//Chunk.SIZE
        cpos = cx,cy
        if cpos not in self.light_chunks:
            self.light_chunks[cpos] = []
        self.light_chunks[cpos].append((*position,brightness))

        for y in range(cy-1,cy+2,1):
            for x in range(cx-1,cx+2,1):
                self.dirty_chunks.add((x,y))


    def update(self):
        if self.dirty_chunks:
            cpos = self.dirty_chunks.pop()
            flooded_chunk = self.flooded_light_chunks[cpos]
            surrounding_lights = []
            for p in getSurroundings(cpos):
                surrounding_lights.extend(self.light_chunks[p])
            x_0 = cpos[0]*Chunk.SIZE
            y_0 = cpos[1]*Chunk.SIZE
            for y in range(Chunk.SIZE):
                for x in range(Chunk.SIZE):
                    light = min(manhattan_distance(lx,ly,x+x_0,y+y_0) for lx,ly,brightness in surrounding_lights)
                    flooded_chunk[x,y] = light


    def getChunkLights(self,cx,cy):
        return self.flooded_light_chunks[(cx,cy)]


            

def getSurroundings(pos:tuple[int,int]):
    cx,cy = pos
    return [(x,y) for y in range(cy-1,cy+2,1) for x in range(cx-1,cx+2,1)]

    