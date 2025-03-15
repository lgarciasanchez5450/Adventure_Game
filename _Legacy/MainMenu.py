from GuiFramework import *
from pygame import event
from Window import Window
from pygame import event
ExitMainMenuEvent = event.Event(event.custom_type())

class MainMenu: 
    def __init__(self,window:Window|None = None) -> None:
        self.window = window or Window((500,500))
        self.window.setName('Game')
        self.base_layer = Layer(self.window.size())
        self.base_layer.resize(self.window.size())
        self.base_layer.space.addObjects(
            BackgroundColor((0,50,50)),
            Aligner(
                AddText(
                    Button((0,0),(50,50),ColorScheme(100,100,100),lambda : event.post(ExitMainMenuEvent)),
                    'Start',(255,255,255),font.SysFont('Arial',20)
                ),
                0.5,0.5
            ),
            Aligner(
                Text((0,0),'Game Title',(255,255,255),font.SysFont('Arial',50)),
                0.5,0.2
            )
        )

    def run(self):
        while True:
            input = getInput()
            if input.quitEvent:
                return self.close(0)
            elif ExitMainMenuEvent.type in input.Events:
                return self.close(2)
            self.base_layer.update(input)
            self.base_layer.draw(self.window.ui_surface)
            Clock().tick(30)
            self.window.draw()
            pygame.display.flip()

    def close(self,ret_code:int):
        base_layer.space.clear()
        self.window.close()
        return ret_code
    

if __name__ == '__main__':
    print('Exit Status:',MainMenu().run())