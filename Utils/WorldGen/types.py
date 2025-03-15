from typing import Protocol
import numpy as np
import numpy.typing as np_typing
class ChunkType(Protocol):
    SIZE:int
    pos:tuple[int,int,int]
    blocks:np_typing.NDArray[np.uint32|np.uint16]
    biome:np_typing.NDArray[np.uint32|np.uint16|np.uint8]
    entities:list

