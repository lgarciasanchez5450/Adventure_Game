
import gc 
gc.disable()
from Constants.Display import *
from Constants.Misc import *
import pygame

import Camera
import Time
import Input 
import UI
import Settings
import Particles
pygame.init()
import general_manager #should take care of everything that chunk/entity manager used to do
import debug
from game_math import Vector2
import Music,Sounds 
import Game_Time
import Main_Menu
Main_Menu.start()
import Events
import Pause_Menu


def onGameAwake():
    global gen
    import Textures
    Textures.init()
    Time.init()
    Music.init()
    Pause_Menu.init()


def onGameStart():
    
    screen = pygame.Surface((WIDTH,HEIGHT))
    Camera.init(screen)
    Sounds.init()
    debug.init(screen)
    Music.start()
    Camera.set_mouse_assist(False)
    player = general_manager.Player((0,0))
    general_manager.spawn_entity(player)
    general_manager.spawn_entity(general_manager.ItemWrapper(Vector2(2,0),general_manager.DivineBow()))
    general_manager.spawn_entity(general_manager.ItemWrapper(Vector2(-2,0),general_manager.Bow()))
    general_manager.spawn_entity(general_manager.ItemWrapper(Vector2(2,2),general_manager.ItemArrowExplosive().setCount(64)))
    Camera.set_focus(player.pos)
    Camera.set_mouse_pull_strength(13)
    #Events.call_OnResize(WINDOW_WIDTH,WINDOW_HEIGHT)
    Game_Time.time_speed = 24   
    Game_Time.start()
    Game_Time.set_time(hour =8)
    Game_Time.update()
    Camera.resize_screen(WINDOW_WIDTH,WINDOW_HEIGHT)
    #pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT),pygame.OPENGL| pygame.DOUBLEBUF|pygame.RESIZABLE) # can be Resizable with no problems
# can be set outside of the game loop
t = gc.collect()
print(t)
del t
while True:
    if Settings.game_state is RUNNING:
        #update each module in order
        #Time
        Time.update() #should be updated before anything else
        Game_Time.update()
        #Input
        Input.update()
        
        #Main Game Loop
        general_manager.step()
        general_manager.update()
        general_manager.update_entities()
        general_manager.manage_chunks()

        Particles.update()
        if Input.KDQueue:
            if 'p' in Input.KDQueue:
                from pympler.asizeof import asizeof
                print(asizeof(general_manager.entity_chunks))
                print(len(general_manager.entity_chunks))
        #Cameras  
        Camera.update()
        Camera.draw_background() 
        Particles.draw()
        Camera.sorted_draw_from_queue()
        Particles.after_draw()
        Particles.anim_draw()
        Camera.draw_collider_queue()
        Camera.draw_UI()
        debug.debug(general_manager.active_entity_count(),(200,200))
        debug.debug(Time.get_frameRateInt())
        Camera.program['light'] = Game_Time.light

        Camera.translate_to_opengl()
        UI.showingUIs[0].draw()
        Camera.flip()

    elif Settings.game_state is SETTINGS:
        Time.update()
        #
        Pause_Menu.update()  
        Camera.flip()
  
    elif Settings.game_state is MAIN_MENU:
        Main_Menu.update()
        if (Main_Menu.loading_for.timeElapsed() > 2): #if has been "loading" for more than 2 seconds start generating the world-
            gen = general_manager.generate_world()

            onGameAwake()
            Settings.game_state = GENERATING_WORLD
    elif Settings.game_state is GENERATING_WORLD:
            try:
                Main_Menu.update()
                chunks_finished, _ = next(gen) #type: ignore
                print(chunks_finished)
                Main_Menu.lb.setDone(chunks_finished) 
            except StopIteration:
                Main_Menu.close()
                onGameStart()
                Settings.game_state = RUNNING

    elif Settings.game_state == CHARACTER_CREATION:
        pass
    elif Settings.game_state == WORLD_SELECT:
        pass

