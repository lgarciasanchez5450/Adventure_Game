
import gc 
gc.disable()
import pygame
pygame.init()


from GameApp import GameApp

state = 1
while True:
    if state == 1:
        state = 2 #make game run
    elif state == 2:
        state = GameApp().run()
    else:
        break


pygame.quit()

