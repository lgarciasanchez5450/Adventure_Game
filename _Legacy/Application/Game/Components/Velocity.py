from ._Component import register
from ...Utils.Math.Vector import Vector2

@register
class Velocity(Vector2):
    pass

inst = Velocity.zero()