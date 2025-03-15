from Utils.Math.Collider import Collider
import glm
class Block:
    def __init__(self,position:tuple[int,int,int],
                 size:tuple[int,int,int],
                 name:str,
    #             hardness:int,
    #             blast_resistance:int
                 ) -> None:
        self.name = name
        self.collider = Collider(glm.vec3(position),size)
        

AIR = 0
STONE = 1
DIRT = 2
GRASS = 3
WATER = 4
NETHERSTONE = 5



blocks = {
    'stone': lambda pos: Block(pos,(1,1,1),'stone')
}