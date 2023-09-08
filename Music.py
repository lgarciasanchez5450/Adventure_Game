from pygame.mixer import music
from os.path import dirname,realpath
from collections import deque
from Constants import MUSIC_FOLDER,STARTING_SOUND_VOLUME
song_queue = deque()

def PATH():
  return dirname(realpath(__file__)) + '\\'




def play_forever(fileName:str):
  music.load(PATH() +MUSIC_FOLDER+'\\'+fileName)
  music.play(-1,0,0)
  
def play(fileName:str):
  print('now playing',fileName)
  music.load(PATH()+MUSIC_FOLDER+'\\'+fileName)
  music.play()

def start():
  play(song_queue[0])

def init(randomize=True):
  music.set_volume(STARTING_SOUND_VOLUME)
  import Sounds,random
  song_queue.extend(Sounds.get_all_music())
  if randomize:
    random.shuffle(song_queue)
   

   
      

def onMusicEnd():
  song_queue.append(song_queue.popleft())
  play(song_queue[0])
    
def skipSong():
  onMusicEnd()



if __name__ == "__main__":
    print('Running Tests on Module Textures')
    import Sounds,time,pygame
    pygame.mixer.init()
    play_forever('Sweden.mp3')
    time.sleep(1)
     


    print('All Tests Passed')