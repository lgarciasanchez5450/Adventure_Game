import typing
import pygame
import pygame.constants as const

if typing.TYPE_CHECKING:
    from _Legacy.Scene import Scene

class HUD:
    def __init__(self,scene:"Scene") -> None:
        self.scene = scene

    def draw(self):
        surf = self.scene.surface_ui
        #draw hp

