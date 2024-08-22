'''
This is the simplest type of village:
It has no walls surrounding it
every building is prebuilt and have no doors
it has no paths connecting buildings
all buildings are of the same type
'''
import numpy as np


class Village:
    buildings = [
        np.array(
            [[1,1,0,1,1],
             [1,0,0,0,1],
             [1,0,0,0,1],
             [1,0,0,0,1],
             [1,1,1,1,1],]
        )
    ]
    
    def __new__(cls,size:tuple[int,int]):
        if min(size) < 100: return None
        return super().__new__(cls)
    
    def __init__(self,size:tuple[int,int]):
        self.size = size
        print("__init__ called!")


Village((100,100))