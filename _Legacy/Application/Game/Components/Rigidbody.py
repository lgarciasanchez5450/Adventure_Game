from ._Component import register
from ...Utils.Math.Collider import Collider
@register
class Rigidbody(Collider):
    def __init__(self) -> None:
        super().__init__(0,0,0,0)

    


inst = Rigidbody()