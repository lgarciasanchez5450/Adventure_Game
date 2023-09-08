import framework
from framework import *
import Settings
from Constants import STARTING_SOUND_VOLUME
import debug
import Music
import UI as User_Interface
import Input
from UI import UI
import Camera
def resume():
    Settings.game_state = Settings.RUNNING
window_space:Window_Space
ui:UI = None
def quit():
    import sys
    sys.exit()

def init():
    '''Called once on setup'''
    global window_space,ui
    ui = UI()
    framework.setSurface(ui.surface)
    framework.setSoundEndEvent(Music.onMusicEnd)
    window_space = Window_Space()
    window_space.background_color = (1,1,1)
    window_space.mainSpace = ScrollingMS()
    window_space.background_color = (1,1,1)
    window_space.mainSpace.music_slider = Slider(20,40,window_space.MSSize[0]-50,8,0,101,lambda x: mixer.music.set_volume((x/100)**2),(100,100,100),(255,255,255),True,starting_value=STARTING_SOUND_VOLUME)
    window_space.mainSpace.resume_button = Button((20,80),150,50,lambda:None,'light grey','grey','dark grey','Resume',20,10,None,escape_unicode,False,resume,'OnUpCommand','white')
    window_space.mainSpace.skip_song_button = Button((200,80),200,50,lambda:None,'light grey','grey','dark grey','Skip Song',20,10,None,None,False,Music.skipSong,'OnUpCommand','white')
    window_space.mainSpace.set_background_color((25,25,25))
    window_space.mainSpace.fps_counter = FPS((5,5))
    window_space.initiate()





#there will be one slider for music, one button to exit, and one button to resume

def update():
    inp = getAllInput()
    Input._update_mouse()
    ui.update()
    inp.mpos = ui.rel_mouse_pos.tuple
    if inp.quitEvent:
        quit()
    window_space.update(inp)
    window_space.draw()
    ui.draw()

