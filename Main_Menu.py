from framework import *
from Colors import * 
from Fonts import *
import Input
from Window import Window
from pygame import event
ExitMainMenuEvent = event.Event(event.custom_type())

class MainMenu: 
    def __init__(self,window:Window|None = None) -> None:
        self.window = window or Window((500,500))
        base_layer.resize(self.window.size())
        base_layer.space.addObjects(
            Aligner(
                AddText(
                    Button((0,0),(50,50),ColorScheme(100,100,100),lambda : toNone(Input.event.post(ExitMainMenuEvent))),
                    'Start',text_color,font.SysFont('Arial',20)
                ),
                0.5,0.5
            ),
            Aligner(
                Text((0,0),'Game Title',text_color,font.SysFont('Arial',50)),
                0.5,0.2
            ),
            BackgroundColor((0,50,50))
        )

    def run(self):
        while True:
            input = Input.getInput()
            if input.quitEvent:
                self.close()
                return 0
            if ExitMainMenuEvent.type in input.Events:
                self.close()
                return 2
            base_layer.update(input)
            base_layer.draw(self.window.ui_surface)
            self.window.draw()
            pygame.display.flip()

    def close(self):
        base_layer.space.clear()
        self.window.close()