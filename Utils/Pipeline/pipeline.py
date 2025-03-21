import typing
from .node import PipelineNode

T_ = typing.TypeVar('T_')
T_2 = typing.TypeVar('T_2')
class Pipeline[A,B]:
    def __init__(self,first:list[PipelineNode[A,T_]],nodes:list[PipelineNode],lasts:list[PipelineNode[T_2,B]]):
        self.firsts = first
        self.lasts = lasts
        self.nodes = nodes

    def queueChunk(self,chunk:A):
        for first in self.firsts:
            first.queueChunk(chunk)
    
    def update(self):
        for first in self.firsts:
            first.update()
        for node in self.nodes:
            node.update()
        for last in self.lasts:
            last.update()
