
from .gpass import GenPass
import numpy as np
from numpy import typing as nptyping
from typing import TYPE_CHECKING
from .types import ChunkType

class Gen:
    def __init__(self):
        self.passes: list[GenPass] = [
            
        ]

    def processChunk(self, chunk:ChunkType): 
        # assert chunk.data

        for pass_ in self.passes:
            pass_.processChunk(chunk)
