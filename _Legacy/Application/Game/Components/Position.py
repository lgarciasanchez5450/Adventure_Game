from ._Component import register
from ...Utils.Math.Vector import Vector2

@register
class Position(Vector2):
    pass

inst = Position.zero()