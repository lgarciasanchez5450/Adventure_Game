from typing import Protocol,Optional,TypeVar

class SystemBase:
    def Start(self): ...
    def Update(self):...
    def End(self): ...
T = TypeVar("T",bound=SystemBase)

systems:list[SystemBase] = []

def register(system):
    systems.append(system)
    return system


