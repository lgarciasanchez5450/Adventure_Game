from pygame import Surface
from Constants import BLOCK_SIZE
import game_math
from Camera import CSurface
import Camera
import collision_area 
from ground import getGround
import Textures
import Settings
class Block:
    
    @staticmethod
    def spawnable_on(ground):
      return True

    def __init__(self,pos,type,block = None):
        hb = Settings.HITBOX_SIZE[type]
        self.collider = game_math.Collider.SpawnOnBlockCenter(*pos,*hb)
        self.pos = game_math.Vector2(*self.collider.center) #hp -> huan pablo
        self.type:str = type
        self.tags = set()
        self.bast_resistance = 0 
        self.hardness = 1
        self.walk_speed_multiplier = 1
        self.surf_offset = Settings.SURFACE_OFFSET[type]
        self.surf = Surface((0,0))

        self.csurface = CSurface(self.surf, self.pos, self.surf_offset)        
        self.incamera = False

    def onLoad(self) -> None: ...

    def onLeave(self) -> None: ...

    def update(self) -> None: ...

    def draw(self) -> None: ...
      
class Tree(Block):
  oak_tex = '03.png'
  @staticmethod
  def spawnable_on(ground) -> bool:
    return ground is Dirt
  #this class is an "obstacle" 
  def __init__(self,pos,ground = None):
    if not Tree.spawnable_on(ground):
        raise RuntimeError(f"Tree was spawned on illegal block: {ground}")
      
    super().__init__(pos,'tree')
    self.surf = Textures.texture[Tree.oak_tex]
    self.csurface.surf = self.surf

       

  def onLoad(self):
    self.incamera = True
    collision_area.add_obstacle(self.collider)
    collision_area.add_physical_object(self)
    
    Camera.add_collider(self.collider)
    Camera.add(self.csurface)
  
  def onLeave(self):
    self.incamera = False
    collision_area.remove_obstacle(self.collider)
    collision_area.remove_physical_object(self)

    Camera.remove_collider(self.collider)

    Camera.remove(self.csurface)


  def update(self):
    pass


class TNT(Block):
  tnt_tex = 'tile395.png'
  @staticmethod
  def spawnable_on(ground):
    return ground is Dirt
  
  def __init__(self, pos, type, block=None):
    super().__init__(pos, type, block)
    self.surf = Textures.texture[TNT.tnt_tex]
    self.csurface.surf = self.surf

  def onLoad(self):
    self.incamera = True
    collision_area.add_obstacle(self.collider)
    collision_area.add_physical_object(self)
    
    Camera.add_collider(self.collider)
    Camera.add(self.csurface)
    
 
  def onLeave(self):
    self.incamera = False
    collision_area.remove_obstacle(self.collider)
    collision_area.remove_physical_object(self)

    Camera.remove_collider(self.collider)

    Camera.remove(self.csurface)


  def update(self):
    pass