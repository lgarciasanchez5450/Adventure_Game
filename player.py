from Constants import *
from game_math import Collider,set_mag,Vector2
from math import floor
from Items import Item
import general_manager
import Settings
import Input
import Time
import Particles
import Camera
import Textures
import Entity
class Player(Entity.Entity):
    def __init__(self,pos):
        super().__init__(pos,'human')

        self.cx = self.pos.x//CHUNK_SIZE
        self.cy = self.pos.y//CHUNK_SIZE
        general_manager.recalculate_chunks(self.cx,self.cy)
        self.set_up_animation()
        Camera.add(self.image)
		# stats


        self.exp = 5000 #dont make attribute points (overused). make exp have another purpose. attribute points can lead to severely op setups and the player getting exactly what they want. 
        # damage timer
        self.can_move = True
        self.attacking = False
        self.vulnerable = True
        self.hurt_time = None

        self.direction = 'right'


    def set_up_animation(self):
        walk_right,walk_left= Textures.import_folder('player/walk',True,(64,64),True)
        idle_right,idle_left = Textures.import_folder('player/idle',True,(64,64),True)
        attack_right,attack_left = Textures.import_folder('player/attack',True,(64,64),True)
        self.walking_particle = Textures.import_folder('Images/particles',False,(PARTICLE_SIZE,PARTICLE_SIZE))[0]
        self.animation.add_state('walk',7,walk_right,walk_left)
        self.animation.add_state('idle',1.5,idle_right,idle_left)
        self.animation.add_state('attack',9,attack_right,attack_left)
        self.animation.set_state('idle')
        self.animation.on_animation_done = self.on_animate_done



    def attack(self):
        self.animation.set_state('attack')

    def _attack(self):
        if self.direction == 'right':
            c = Collider(self.pos.x+.2,self.pos.y-.5,.5,1)
        elif self.direction == 'left':
            c = Collider(self.pos.x-.7,self.pos.y-.5,.5,1)
        #camera.queue_draw_hitbox(c)
        return
        for enemy in self.hit(c):
            break
            enemy.take_damage(self.atk())

    def input(self): #Time.deltaTime is in seconds
        if Input.m_1 and self.animation.state != 'attack':
            self.attack()
        
        if Input.space_d:
            general_manager.spawn_item(Item.as_entity(self.pos.copy()))
        
        if self.animation.state != 'attack':
            self.vel.x,self.vel.y =  set_mag(Input.d-Input.a,Input.s-Input.w,self.speed * Time.deltaTime)
        else:
            self.vel.reset() #set 

        if self.vel.x > 0:
            self.animation.direction = 'right' 
        elif self.vel.x < 0:
            self.animation.direction = 'left'

  

    def move(self):
        super().update()
            
        #detect if in new chunk
        if self.pos.x//CHUNK_SIZE != self.cx:
            #in new chunk
            self.cx = floor(self.pos.x)//CHUNK_SIZE
            self.cy = floor(self.pos.y)//CHUNK_SIZE
            general_manager.recalculate_chunks(self.cx,self.cy)
            
        elif self.pos.y//CHUNK_SIZE != self.cy:
            #in new chunk
            self.cx = floor(self.pos.x)//CHUNK_SIZE
            self.cy = floor(self.pos.y)//CHUNK_SIZE
            general_manager.recalculate_chunks(self.cx,self.cy)

    
    def in_chunk(self,cx,cy):
        '''accepts coords in world chunk position'''
        return (cx == self.cx) and (cy == self.cy)

    def on_animate_done(self):
        if self.animation.state == 'attack':
            if self.vel:
                self.animation.set_state('walk')
            else:
                self.animation.set_state('idle')


            
    def animate(self):
        if self.vel and self.animation.state == 'idle': self.animation.set_state('walk')
        elif not self.vel and self.animation.state == 'walk': self.animation.set_state('idle')
        self.animation.animate() #meat and bones of what 'animate' should actually do
        if self.animation.state == 'attack' and self.animation.frames_in_state == 4 and self.animation.previous_frames_in_state == 3:
            self._attack()

        if self.vel and not ((Time.time*1000).__trunc__() % 100):
            #spawn a particle
            Particles.spawn(self.pos + Vector2(0,.2),Vector2.random/1,self.walking_particle,.5)

    
    def collect_items(self):
        pass

    def update(self):
        self.input()
        self.move()
        self.animate()
    

''' Functions which used to be part of the player class but arent necessary right now   
    def take_damage(self,damage:int|float,type:str):
        damage /=  sqrt(log2(self.defense))
        print(f'Taking {damage} damage in the form of {type}')
        self.health -= damage

    def atk(self):
        dmg = 1 #
        return dmg * log2(self.strength)
'''