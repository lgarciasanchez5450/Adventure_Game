import pygame
from game_math import *
import Camera
from Constants import *
import SFX
import Time
import Inventory
import Animation
import Settings
import Textures
import chunkmanager


class Entity:
    def __init__(self,pos,species):
        self.pos = Vector2(*pos)
        self.vel = Vector2.zero
        self.species = species
        self.image = Camera.CSurface(Textures.texture['null.png'],self.pos,Settings.SURFACE_OFFSET[species])
        self.collider = Collider(0,0,*Settings.HITBOX_SIZE[species])
        self.animation = Animation.Animation(self.image)
        self.inventory = Inventory.Inventory(Settings.INVENTORY_SPACES_BY_SPECIES[species])

        #Stats
        
        self.stats = Settings.STATS_BY_SPECIES[species].copy()
        
        self.exp = 5000 #dont make attribute points (overused). make exp have another purpose. attribute points can lead to severely op setups and the player getting exactly what they want. 
        speed = self.stats['speed'] # convert from blocks/millisecond -> blocks per second
        self.speed = Settings.MAX_SPEED_BY_SPECIES[species] * speed / (speed + 100)
        self.total_health = self.stats['constitution'] * 5 + self.stats['strength'] + self.stats['stamina']
        self.health = self.total_health
        self.strength = self.stats['strength'] * 5 + self.stats['constitution'] + self.stats['stamina']
        self.energy = self.stats['energy']
        


        # damage timer
        self.vulnerable = True
        self.hurt_time = None

        self.direction = 'right'



    def onLoad(self): 
        Camera.add(self.image)
    def onLeave(self):
        Camera.remove(self.image)


    def update(self):
        #move x rect 
        self.collider.move_x(self.vel.x) # move in world coordinates
        chunkmanager.collision_horizontal(self.collider,self.vel.x)
        #move y rect 
        self.collider.move_y(self.vel.y) # move in world coordinates
        chunkmanager.collision_vertical(self.collider,self.vel.y)
        self.pos.from_tuple(self.collider.center)

    def get_damage_reducted(self,damage:int|float,type:str) -> float:
        '''Returns damage resisted'''
        defense = self.stats['defense']
        damage_reduction = damage * defense/ (defense+100) 
        return damage - damage_reduction
    
    def take_damage(self,damage:float,type:str) -> None:
        damage = self.get_damage_reducted(damage,type)
        self.health -= damage
        if self.health <= 0:
            print(f'Entity of Species {self.species} has died')
    
    def get_energy_multiplier(self) -> float:
        return .5 * ((self.energy/self.stats['energy'] + 1))

    def get_attack_damage(self) -> float:
        '''Returns final attack damage'''
        #get base damage
        damage = self.stats['attack']

        #get total inventory added damage
        damage += self.inventory.added_atk

        damage *= 1 + self.stats['strength'] / 100 * self.get_energy_multiplier()

        return damage

    def get_attack_type(self) -> str:
        return PHYSICAL_DAMAGE



class Spirit(Entity):
    right_idle,left_idle = Textures.import_folder('Images/enemies/spirit/idle',True,(64,64),True)
    def __init__(self,pos):
        super().__init__(pos,'spirit')
        self.animation.add_state('idle',8,Spirit.right_idle,Spirit.left_idle)        

    def onLoad(self):
        print('Loading Spirit')
        return super().onLoad()
    
