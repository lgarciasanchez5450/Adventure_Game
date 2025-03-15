from ...Utils.Math.Vector import Vector2
from .... import Window
from .. import Entities
from ..Components import Renderable, Position
from ..Constants import BLOCK_SIZE
from .Systems import register


@register
class Renderer:
    _renderable_comp = Renderable.inst
    _position_comp = Position.inst
    #Called before First Frame
    @classmethod
    def Start(cls): 
        cls.window = Window.window
        cls.camera_position = Vector2.zero()

    @staticmethod
    def is_withing_frustrum():
        pass
    
    #Called Every Frame
    @classmethod
    def Update(cls):
        for renderable,position in Entities.findAllComponentSets(cls._renderable_comp,cls._position_comp):
            cls.window.world_surface.blit(renderable.surface,((position-cls.camera_position)*BLOCK_SIZE+Vector2(*cls.window.size())/2).tuple)
    
    #Called After Last Frame
    @classmethod
    def End(cls): 
        pass

