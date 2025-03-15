from ._Component import register

@register
class Health:
    __slots__ = 'health','full_health'
    def __init__(self,health:int,full_health:int) -> None:
        self.health = health
        self.full_health = full_health

inst = Health(0,0)