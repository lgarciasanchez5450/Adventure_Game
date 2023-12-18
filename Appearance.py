class Appearance:
    """What an entity of 'somthing' looks like in game
    to be used for AI of npc's"""
    __slots__ = 'color','size','shape','species'
    def __init__(self,color:float,size:float,shape:float,species:str):
        self.color = color
        self.size = size
        self.shape = shape
        self.species = species

    def looks_like(self,other:"Appearance",tolerance:float): 
        '''A very simple model function to tell what others would look like in the future'''
        return abs(other.color - self.color) < tolerance and abs(other.size - self.size) < tolerance and abs(other.size - self.size) < tolerance

    def copy(self):
        return Appearance(self.color,self.size,self.shape,self.species)
