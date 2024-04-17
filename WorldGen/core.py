
from .gpass import GenPass
import numpy as np
from numpy import typing as nptyping
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..general_manager import Chunk


class Gen:
    def __init__(self):
        self.passes: list[GenPass] = [
            
        ]

    def processChunk(self, chunk:'Chunk'): 
        # assert chunk.data

        for pass_ in self.passes:
            pass_.processChunk(chunk)
