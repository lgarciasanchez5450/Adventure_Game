from typing import TYPE_CHECKING
from ..Utils.Math.Vector import Vector2
from ..Utils.Math.Collider import Collider
from .. import Textures
from . import Systems
from . import InputGame
from . import GameTime

from .Entities import *

if TYPE_CHECKING:
    from ...GuiFramework.Input import Input



def Start():
    m_startSystems()
def Update(input:'Input'):
    InputGame.update(input)
    GameTime.update()
    m_updateSystems()

def m_updateInput(input:'Input'):
    InputGame.update(input)
def m_startSystems():
    for s in Systems.systems:
        s.Start()
def m_endSystems():
    for s in Systems.systems:
        s.End()
def m_updateSystems():
    for s in Systems.systems:
        s.Update()
