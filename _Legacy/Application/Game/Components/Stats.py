from ._Component import register

@register
class Stats:
    __slots__ = 'strength','speed','defense','constitution','energy','stamina'
    def __init__(self):
        self.strength = 0
        self.speed = 0
        self.defense = 0
        self.constitution = 0
        self.energy = 0
        self.stamina = 0

inst = Stats()