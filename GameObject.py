from Utils.Math.Vector import Vector2
from Camera import CSurface
import Camera
from GameScreen.Appearance import Appearance
from sys import intern
class GameObject:
    '''This class is the base class of which every single diagetic object in the game MUST derive from.'''
    __slots__ = 'pos','dead','csurface','typeid'
    def __init__(self,pos:Vector2,typeid:str) -> None:
        self.pos = pos
        self.dead = False
        self.typeid = intern(typeid)
        self.csurface:CSurface

    def update(self): ...

    def take_damage(self,damage:int,type:str,appearance:Appearance|None = None): ...

    def onLoad(self):
        Camera.add(self.csurface)

    def onLeave(self):
        Camera.remove(self.csurface)

    def onDeath(self):
        '''Returns whether this is a true or false death
        A false death happens when an object gets killed multiple times in one frame
         and onDeath gets called multiple times. 
        After the first call to onDeath
         all other calls are considered false deaths '''
        if self.dead: return False
        self.onLeave()
        self.dead = True
        return True

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} : {self.typeid}"
