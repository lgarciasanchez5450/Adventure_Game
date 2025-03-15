from ._Component import register
from pygame import Surface

@register
class Renderable:
    __slots__ = 'surface','offset'
    def __init__(self) -> None:
        self.surface = Surface((0,0))
        self.offset = (0,0)


inst = Renderable()