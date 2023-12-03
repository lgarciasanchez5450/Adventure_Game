from os import walk
from os.path import dirname,realpath
from pygame import mixer
import pygame
from Constants import MUSIC_FOLDER,SOUND_FOLDER

def PATH():
  return dirname(realpath(__file__)) + '\\'

def is_sound(file:str) -> bool:
    return file.endswith(('ogg','mp3','wav'))

def get_all_music() -> list[str]:
  for _,_,files in walk(PATH()+MUSIC_FOLDER):
    return list(filter(is_sound,files))
  return []
sounds = {}
def import_sounds(folder_path:str):
    sounds_found = []
    for _dir,_root,files in walk(PATH()+folder_path):
        for file in files:
            if is_sound(PATH() +file): #only will get image files
                full_path = PATH() + folder_path + '/' + file

                sound = mixer.Sound(open(full_path)) 
            

                sounds_found.append(sound)

                sounds[file] = sound
    if len(sounds_found) == 0:
        print(f"Warning, folder {folder_path} has no sounds")
    return sounds_found


def init():
    pygame.MUSICEND = pygame.USEREVENT + 1 #type: ignore
    mixer.music.set_endevent(pygame.MUSICEND) #type: ignore
    import_sounds(SOUND_FOLDER)


if __name__ == "__main__":
    print('Running Tests on Module Textures')
    import pygame
    pygame.init()
    init()
    get_all_music()

    print('All Tests Passed')