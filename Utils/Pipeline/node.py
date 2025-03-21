import typing
from collections import deque

class PipelineNode[I,O]:
    def __init__(self,out:deque[O]):
        self.queued:deque[I] = deque()
        self.out:deque[O] = out

    def queueChunks(self,chunks:typing.Iterable[I]):
        self.queued.extend(chunks)
    
    def queueChunk(self,chunk:I):
        self.queued.append(chunk)

    def update(self):
        pass