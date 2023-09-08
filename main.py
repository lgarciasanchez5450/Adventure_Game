
from memory_profiler import profile
@profile
def _():pass
import gc
gc.disable()
from Constants import *
import pygame


display = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT),pygame.OPENGL| pygame.DOUBLEBUF|pygame.RESIZABLE) # can be Resizable with no problems

import Textures


Textures.init()

screen = pygame.Surface((WIDTH,HEIGHT))
import Camera
Camera.init(screen)
import Time

import Input
import debug
import general_manager #should take care of everything that chunk/entity manager used to do

import Particles

import Game_Time

import Music,Sounds 

import UI

import Settings
import Pause_Menu

Pause_Menu.init()
Sounds.init()
debug.init(screen)
Time.init()
Camera.set_mouse_pull_strength(13)
Camera.set_tracking('smooth')
Camera.set_mouse_assist(False)
player = general_manager.Player((0,0))
general_manager.spawn_entity(player)
Camera.set_focus(player.pos)

Music.init()
Music.start()
Game_Time.time_speed = 24   
Game_Time.start()
Game_Time.set_time(hour =8)
Game_Time.update()
print(Game_Time.game_time())

#general_manager.spawn_entity(Entity.Spirit((0,0)))
#general_manager.spawn_entity(general_manager.Spirit((5,0)))
Camera.program['tex'] = 0 # can be set outside of the game loop
t = gc.collect()
print(t)
while True:
    if Settings.game_state is RUNNING:

        #update each module in order

        #Time
        Time.update() #should be updated before anything else
        Game_Time.update()
        #Input
        Input.update()
        
        if Input.rctrl:
            print(gc.collect())
        #Main Game Loop
        general_manager.step()
        general_manager.update()
        general_manager.update_entities()
        general_manager.manage_chunks()


        Particles.update()


        #Cameras
        Camera.update()
        Camera.draw_background() 
        Particles.draw()
        Camera.sorted_draw_from_queue()
        Particles.after_draw()
        Particles.anim_draw()
        Camera.draw_collider_queue()
        Camera.draw_UI()
        debug.debug(Time.get_frameRateInt())
        Camera.program['light'] = Game_Time.light

        Camera.translate_to_opengl()
        UI.current_ui.draw()
        Camera.flip()


    elif Settings.game_state is SETTINGS:
        Time.update()
        #
        Pause_Menu.update()
        Camera.flip()

    elif Settings.game_state is MAIN_MENU:
        pass


