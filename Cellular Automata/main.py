import numpy as np
import renderer

def conways_game_of_life_step(map:np.ndarray):
    
    rleft = np.roll(map,-1, axis = 1)
    rright = np.roll(map,1, axis = 1)
    rtop = np.roll(map,-1, axis = 0)
    rbottom = np.roll(map,1, axis = 0)

    sums = rleft.astype(np.int32) + rright + rtop + rbottom + np.roll(rleft,-1,axis=0) + np.roll(rright,-1,axis=0) + np.roll(rleft,1,axis=0) + np.roll(rright,1,axis=0) 
    todie = np.logical_and(np.logical_or(sums < 2, sums > 3),map)
    tolive = np.logical_or(np.logical_and(np.logical_or(sums == 2,sums == 3),map),np.logical_and(sums==3,~map))

    
    map[todie] = False
    map[tolive] = True


    
    return map

def remove_infill_step(map:np.ndarray):
    rleft = np.roll(map,-1, axis = 1)
    rright = np.roll(map,1, axis = 1)
    rtop = np.roll(map,-1, axis = 0)
    rbottom = np.roll(map,1, axis = 0)

    sums = rleft.astype(np.int32) + rright + rtop + rbottom + np.roll(rleft,-1,axis=0) + np.roll(rright,-1,axis=0) + np.roll(rleft,1,axis=0) + np.roll(rright,1,axis=0) 
    takeout = sums > 7
    map[takeout] = 0
    return map

def smooth_dots(map:np.ndarray):
    rleft = np.roll(map,-1, axis = 1)
    rright = np.roll(map,1, axis = 1)
    rtop = np.roll(map,-1, axis = 0)
    rbottom = np.roll(map,1, axis = 0)

    sums = rleft.astype(np.int32) + rright + rtop + rbottom + np.roll(rleft,-1,axis=0) + np.roll(rright,-1,axis=0) + np.roll(rleft,1,axis=0) + np.roll(rright,1,axis=0) 
    fill = sums >6
    map[fill] = 1
    return map

def remove_bumps(map:np.ndarray):
    rleft = np.roll(map,-1, axis = 1)
    rright = np.roll(map,1, axis = 1)
    rtop = np.roll(map,-1, axis = 0)
    rbottom = np.roll(map,1, axis = 0)

    sums = rleft.astype(np.int32) + rright + rtop + rbottom + np.roll(rleft,-1,axis=0) + np.roll(rright,-1,axis=0) + np.roll(rleft,1,axis=0) + np.roll(rright,1,axis=0) 
    fill = sums <2
    map[fill] = 0
    return map

def make_room_step(map:np.ndarray):
    two_lefts = (np.roll(map,1,axis = 0).astype(np.uint8) + np.roll(map,2,axis=0)) // 2
    two_ups = (np.roll(map,1,axis = 1).astype(np.uint8) + np.roll(map,2,axis=1)) // 2
    two_rights = (np.roll(map,-1,axis = 0).astype(np.uint8) + np.roll(map,-2,axis=0)) // 2
    two_downs =  (np.roll(map,-1,axis = 1).astype(np.uint8) + np.roll(map,-2,axis=1)) // 2

    only_left = np.logical_and(two_lefts, ~np.logical_or(two_ups,np.logical_or(two_rights,two_downs)))
    only_right = np.logical_and(two_rights, ~np.logical_or(two_ups,np.logical_or(two_lefts,two_downs)))
    only_up = np.logical_and(two_ups, ~np.logical_or(two_rights,np.logical_or(two_lefts,two_downs)))
    only_downs = np.logical_and(two_downs,~np.logical_or(two_rights,np.logical_or(two_lefts,two_ups)))
    check = np.logical_or(np.logical_or(only_left,only_right),np.logical_or(only_up,only_downs))    
    return check

def cellular_automata_step(map:np.ndarray):
    return map


map = np.zeros((150,150),np.bool_)
import random
seed = 8
random.seed(seed)
for i in range(map.shape[0]):
    for j in range(map.shape[1]):
        map[i,j] = random.randint(0,10) //3.9
import time
renderer.render(map.astype(np.int32)* 100)
def do_thing(map:np.ndarray):

    for i in range(5):
        map = make_room_step(map)
    map = smooth_dots(map)
    map = remove_bumps(map)
    map = smooth_dots(map)
    map = remove_bumps(map)
    map = remove_infill_step(map)

    return map

#time.sleep(2)
while True:
    for event in renderer.pygame.event.get():
        if event.type == renderer.pygame.QUIT:
            quit()
        elif event.type == renderer.pygame.MOUSEBUTTONDOWN:
            if event.button == 1:   
                map = cellular_automata_step(map)
                renderer.render(map.astype(np.int32) * 100)
        elif event.type == renderer.pygame.KEYDOWN:
            if event.key == renderer.pygame.K_SPACE:
                print('doint hing')
                map =  do_thing(map)
                renderer.render(map.astype(np.int32) * 100)
        elif event.type == renderer.pygame.MOUSEWHEEL:
            seed += event.y
            renderer.pygame.display.set_caption(str(seed))

            random.seed(seed)
            for i in range(map.shape[0]):
                for j in range(map.shape[1]):
                    map[i,j] = random.randint(0,10) //4
            renderer.render(map.astype(np.int32)* 100)

        


