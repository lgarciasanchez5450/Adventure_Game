from Main_Menu_Framework import Button, Picture, Surface, Vector2, BLOCK_SIZE,Stopwatch, LoadingBar, Textbox

import Camera, pygame,Input, Events,Time
from Constants.Generation import TOTAL_GENERATED_CHUNKS
    #Camera-Viewpoints
main_view_pos = Vector2.zero

play_view_pos = Vector2(0,-8)

loading_for = Stopwatch()
def start():
    global p,b,lb,lt
    pygame.MUSICEND = pygame.USEREVENT + 1  # type: ignore
    screen = pygame.display.set_mode((500,500),pygame.OPENGL| pygame.DOUBLEBUF|pygame.RESIZABLE) 
    pygame.font.init()
    Camera.init(screen)
    Events.call_OnResize(500,500)
    Camera.set_tracking('smooth')
    Camera.program['light'] = 1.0
    Camera.program['tex'] = 0 
    Time.init()
    Camera.set_focus(main_view_pos)
        
    def startLoad():
        Camera.set_focus(play_view_pos)
        loading_for.start()


    myFont = pygame.font.SysFont("Arial",20)

    playTextSurface = Surface((BLOCK_SIZE,BLOCK_SIZE))
    playText = myFont.render('Play',True,(240,240,240))
    playTextSurface.blit(playText,((playTextSurface.get_width()-playText.get_width())//2, (playTextSurface.get_height()-playText.get_height())//2))

    loadingSurf1 = Surface((500,500))
    loadingSurf2 = Surface((500,500))
    loadingSurf3 = Surface((500,500))
    loadingSurf4 = Surface((500,500))
    text1 = myFont.render('Loading',True,'light grey')
    text2 = myFont.render('Loading.',True,'light grey')
    text3 = myFont.render('Loading..',True,'light grey')
    text4 = myFont.render('Loading...',True,'light grey')
    loadingSurf1.blit(text1,(loadingSurf1.get_width()//2 - text1.get_width()//2,loadingSurf1.get_height()//2 - text1.get_height()//2))
    loadingSurf2.blit(text2,(loadingSurf2.get_width()//2 - text2.get_width()//2,loadingSurf2.get_height()//2 - text2.get_height()//2))
    loadingSurf3.blit(text3,(loadingSurf3.get_width()//2 - text3.get_width()//2,loadingSurf3.get_height()//2 - text3.get_height()//2))
    loadingSurf4.blit(text4,(loadingSurf4.get_width()//2 - text4.get_width()//2,loadingSurf4.get_height()//2 - text4.get_height()//2))

    b = Button(main_view_pos,Vector2(1,1)).setOnPress(startLoad).setCustomFrames((playTextSurface,))
    p = Picture(play_view_pos,Vector2(500,500)).setCustomFrames((loadingSurf1,loadingSurf2,loadingSurf3,loadingSurf4),2)
    lb = LoadingBar(play_view_pos.moved_by(0,2),Vector2(300,30)).setMax(TOTAL_GENERATED_CHUNKS)
    lt = Textbox(play_view_pos.moved_by(-2.3,1.3),pygame.font.SysFont("Arial",13)).setText('')
    del playTextSurface,playText,loadingSurf1,loadingSurf2,loadingSurf3,loadingSurf4,text1,text2,text3,text4




def update():
    Camera.screen.fill('white')
    Time.update()
    Input.update()
    b.update()
    p.update()
    lb.update()
    Camera.update()
    Camera.sorted_draw_from_queue()
    Camera.translate_to_opengl()
    Camera.flip()
    
def close():
    loading_for.stop()
    loading_for.reset()
    b.onLeave()
    p.onLeave()
    lt.onLeave()
    lb.onLeave()


if __name__ == '__main__':
    while 1:
        update()

