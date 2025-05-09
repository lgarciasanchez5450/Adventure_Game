from .SceneBehaviour import *
from Systems.ChunkManager import ChunkManager

class World(SceneBehaviour):
    
    def __init__(self):
        self.chunk_manager = ChunkManager()
