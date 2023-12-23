
#import gc 
#gc.disable()
from Constants.Display import *
from Constants.Misc import *
import Constants

import pygame

import Camera
import Time
import Input 
import Settings
import Particles
pygame.init()
import UI
import general_manager #should take care of everything that chunk/entity manager used to do
import debug
from game_math import Vector2, GAME_PATH

import Music,Sounds 
import Game_Time
import Main_Menu
Main_Menu.start()
import Events
import Pause_Menu
import Textures
import Items

def onGameAwake():
    global gen
    Textures.initInThread()
    Time.init()
    Music.init()
    Pause_Menu.init()

def onGameStart():
    
    screen = pygame.Surface((WIDTH,HEIGHT))
    Camera.init(screen)
    Camera.using_max_camera_distance = True
    Camera.using_min_camera_distance = True
    Sounds.init()
    debug.init(screen)
    Music.start()
    Camera.set_mouse_assist(False)
    global player
    player = general_manager.Player(Vector2(0,0))

    general_manager.spawn_entity(player)
    general_manager.spawn_entity(general_manager.ItemWrapper(Vector2(2,0),Items.DivineBow()))
    general_manager.spawn_entity(general_manager.ItemWrapper(Vector2(-2,0),Items.Bow()))
    general_manager.spawn_entity(general_manager.ItemWrapper(Vector2(2,2),Items.ItemArrowFunny().setCount(64)))
    general_manager.spawn_item(Items.SpeedPotion(),Vector2(1,0),Vector2(0,2))
    Camera.set_focus(player.pos)
    Camera.set_mouse_pull_strength(13)
    #Events.call_OnResize(WINDOW_WIDTH,WINDOW_HEIGHT)
    Game_Time.time_speed = 24   
    Game_Time.start()
    Game_Time.set_time(hour =8)
    Game_Time.update()
    Camera.resize_screen(WINDOW_WIDTH,WINDOW_HEIGHT)
    #pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT),pygame.OPENGL| pygame.DOUBLEBUF|pygame.RESIZABLE) # can be Resizable with no problems
# can be set outside of the game loop+
    
#t = gc.collect()
#print(t)
#del t
while True:
    while Settings.game_state is RUNNING:
        #update each module in orders
        #Time
        Time.update() #should be updated before anything else
        Game_Time.update()
        #Input
        Input.update()
        #print(Input.m_pos_normalized)
        #print(Camera.world_position_from_normalized(Input.m_pos_normalized))
        #Main Game Loop
        general_manager.step()
        general_manager.update()
        general_manager.update_entities()
        general_manager.manage_chunks()
        general_manager.update_explosions()

        Particles.update()
        if Input.KDQueue:
            if 'p' in Input.KDQueue:
                from pympler.asizeof import asizeof
                print(asizeof(general_manager.entity_chunks))
                print(len(general_manager.entity_chunks))
        #Cameras  
        Camera.update()
        #print((Camera.screen_position(player.pos))) #type: ignore
        Camera.draw_background() 
        Particles.draw()
        Camera.sorted_draw_from_queue()

        Camera.draw_collider_queue()
        general_manager.draw_explosions()
        Camera.draw_UI()
        debug.debug(general_manager.active_entity_count(),(200,200))
        debug.debug(Time.get_frameRateInt())
        UI.showingUIs[0].draw()
        Camera.program['light'] = Game_Time.light

        Camera.translate_to_opengl()
        Camera.flip()

    while Settings.game_state is SETTINGS:
        Time.update()
        #
        Pause_Menu.update()  
        Camera.flip()
  
    while Settings.game_state is MAIN_MENU:
        Main_Menu.update()
        if (Main_Menu.loading_for.timeElapsed() > 2): #if has been "loading" for more than 2 seconds start generating the world-
            Main_Menu.lb.setMax(108)
            onGameAwake()
            Settings.game_state = GENERATING_WORLD
    while Settings.game_state is GENERATING_WORLD:
            try:
                #First try to see if we need to import Texturesee
                if not Textures.done_loading:
                    Main_Menu.lt.setText(Textures.current_load_name.removeprefix(GAME_PATH))
                    Main_Menu.lb.setDone(Textures.loaded_counter)
                    Textures.ready_for_next = True
                else: 
                    if Textures.loaded_counter:
                        print('changing to generation')
                        gen = general_manager.generate_world()
                        Main_Menu.lb.setMax(Constants.TOTAL_GENERATED_CHUNKS).setDone(0)
                        Main_Menu.lt.setText('')
                        Textures.loaded_counter = 0
                    chunks_finished, _ = next(gen) #type: ignore
                    #print(chunks_finished)
                    Main_Menu.lb.setDone(chunks_finished) 
                Main_Menu.update()
            except StopIteration:
                Main_Menu.close()
                onGameStart()
                Settings.game_state = RUNNING

    while Settings.game_state == CHARACTER_CREATION:
        pass
    while Settings.game_state == WORLD_SELECT:
        pass


while True:
    while Settings.game_state is RUNNING:
        #do game logic
        pass
    
