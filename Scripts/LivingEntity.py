
import glm
from Scripts.Entity import Entity
from Constants import Damage

class AliveEntity(Entity):
    abstract = True
    # __slots__ = 'actions','pickup_range','inventory','armour_inventory','stats','exp','max_speed','total_health','defense','regen_multiplier','health','strength','max_energy', \
    # 'energy','attack_speed','time_between_attacks','time_to_attack','time_to_regen','regen_time','vision_collider','vision_squared','states','ground','invulnerability_time', \
    # 'time_til_vulnerable','direction','extra_speed','extra_speed_sum','extra_total_health','extra_total_health_sum','extra_regen','extra_regen_sum','extra_strength' ,\
    # 'extra_strength_sum','extra_energy','extra_energy_sum','extra_defense','extra_defense_sum','effects','state','healthbar'
    
    def __init__(self,scene,position:tuple[int,int,int],size:tuple[float,float,float]|glm.vec3,health:float,max_health:float):
        super().__init__(scene,position,size)
        self.health = health
        self.max_health = max_health
        self.face_dir = glm.vec3(0,0,0)
        self.forward = glm.vec3(0,0,0)
        self.right = glm.vec3(0,0,0)
        self.up = glm.vec3(0,1,0)
        
        # self.pickup_range = max(*Settings.HITBOX_SIZE[self.species]) * half_sqrt_2 # just a shortcut for finding the length to the corner of a box from the middle when you only know a side length
        # self.inventory = UniversalInventory(Settings.INVENTORY_SPACES_BY_SPECIES[self.species],self)
        # self.armour_inventory = ArmorInventory(*Settings.ARMOUR_SLOTS_BY_SPECIES[self.species])
        # #Stats
        # self.stats = Settings.STATS_BY_SPECIES[self.species].copy()
        # self.exp = 5000 #dont make attribute points (overused). make exp have another purpose. attribute points can lead to severely op setups and the player getting exactly what they want. 
        # self.max_speed = Settings.MAX_SPEED_BY_SPECIES[self.species] 
        # speed = self.stats['speed'] 
        # self.speed = self.max_speed * speed / (speed + 100)
        # self.total_health = self.stats['constitution'] * 5 + self.stats['strength'] + self.stats['stamina']
        # assert isinstance(self.stats['defense'],int)
        # self.defense = self.stats['defense']
        # self.regen_multiplier = self.stats['constitution'] + self.stats['strength']
        # self.regen_multiplier = self.regen_multiplier / (self.regen_multiplier + 100) + 1
        # self.health = self.total_health
        # self.strength = self.stats['strength'] * 5 + self.stats['constitution'] + self.stats['stamina']
        # self.max_energy = self.stats['energy']
        # assert isinstance(self.stats['energy'],int)
        # self.energy = self.stats['energy']
        # self.attack_speed = self.energy / 10
        # self.time_between_attacks = 1/self.attack_speed
        # self.time_to_attack = self.time_between_attacks
        # self.time_to_regen = 0.0 # regen timer
        # self.regen_time = 1.0 # how long in seconds should we wait between regen ticks
        # self.vision_collider = Collider(0,0,Settings.VISION_BY_SPECIES[self.species]*2,Settings.VISION_BY_SPECIES[self.species]*2)
        # self.vision_squared = Settings.VISION_BY_SPECIES[self.species] ** 2
        # self.states = []
        # self.ground:ground.Ground = ground.Invalid()
        # damage timer
        self.invulnerability_time = 0.5
        self.time_til_vulnerable = 0.0

        self.direction = 'right'
        
        # self.extra_speed:dict[str,float] = {}; self.extra_speed_sum = 0.0
        # self.extra_total_health:dict[str,int] = {}; self.extra_total_health_sum = 0.0
        # self.extra_regen:dict[str,float] = {}; self.extra_regen_sum = 0.0
        # self.extra_strength:dict[str,int] = {}; self.extra_strength_sum = 0.0
        # self.extra_energy:dict[str,int] = {}; self.extra_energy_sum = 0.0
        # self.extra_defense:dict[str,int] = {}; self.extra_defense_sum = 0.0

        # self.effects:list[EntityEffect] = []



    def takeDamage(self,damage:float,type:Damage.DamageType):
        if self.time_til_vulnerable < 0 or type is Damage.INTERNAL_DAMAGE: 
            self.health -= damage
            if self.health <= 0:
                self.dead = True
                self.health = 0        

    ### SET STATS ###
    
    # def setStatSpeed(self,newSpeed:int):
    #     self.stats['speed'] = newSpeed
    #     #update speed
    #     speed = self.stats['speed'] 
    #     self.speed = self.max_speed * speed / (speed + 100)

    # def setStatConstitution(self,newConstitution:int):
    #     self.stats['constitution'] = newConstitution
    #     self.strength = self.stats['strength'] * 5 +newConstitution + self.stats['stamina']
    #     self.regen_multiplier = newConstitution + self.stats['strength']
    #     self.regen_multiplier = self.regen_multiplier / (self.regen_multiplier + 100) + 1

    # def setStatStrength(self,newStrength:int):
    #     self.stats['strength'] = newStrength
    #     self.strength = newStrength * 5 + self.stats['constitution'] + self.stats['stamina']
    #     self.regen_multiplier = self.stats['constitution'] + newStrength
    #     self.regen_multiplier = self.regen_multiplier / (self.regen_multiplier + 100) + 1

    # def setStatStamina(self,newStamina:int):
    #     self.stats['stamina'] = newStamina
    #     self.strength = self.stats['strength'] * 5 + self.stats['constitution'] + newStamina // 2

    # def setStatEnergy(self,newEnergy:int):
    #     self.stats['energy'] = newEnergy
    #     self.max_energy = newEnergy

    # def setStatDefense(self,newDefense:int):
    #     self.stats['defense'] = newDefense
    
    # def setStatAttack(self,newAttack:int):
    #     self.stats['attack'] = newAttack

    # ### SET ADDED STATS ###

    # def setExtraStatSpeed(self,tag:str,addedSpeed:float):
    #     self.extra_speed[tag] = addedSpeed
    #     self.extra_speed_sum = sum(self.extra_speed.values())

    # def setExtraStatTotalHealth(self,tag:str,addedTotalHealth:int):
    #     self.extra_total_health[tag] = addedTotalHealth
    #     self.extra_total_health_sum = sum(self.extra_total_health.values())

    # def setExtraStatRegen(self,tag:str,addedRegen:float):
    #     self.extra_regen[tag] = addedRegen
    #     self.extra_regen_sum = sum(self.extra_regen.values())

    # def setExtraStatStrength(self,tag:str,addedStrength:int):
    #     self.extra_strength[tag] = addedStrength
    #     self.extra_strength_sum = sum(self.extra_strength.values())

    # def setExtraStatEnergy(self,tag:str,addedEnergy:int):
    #     self.extra_energy[tag] = addedEnergy
    #     self.extra_energy_sum = sum(self.extra_energy.values())
    
    # def setExtraStatDefense(self,tag:str,addedDefense:int):
    #     self.extra_defense[tag] = addedDefense
    #     self.extra_defense_sum = sum(self.extra_defense.values())
    
    # ### REMOVE ADDED STATS ###
   
    # def removeExtraStatSpeed(self,tag:str):
    #     del self.extra_speed[tag]
    #     self.extra_speed_sum = sum(self.extra_speed.values())

    # def removeExtraStatTotalHealth(self,tag:str):
    #     del self.extra_total_health[tag]
    #     self.extra_total_health_sum = sum(self.extra_total_health.values())

    # def removeExtraStatRegen(self,tag:str):
    #     del self.extra_regen[tag]
    #     self.extra_regen_sum = sum(self.extra_regen.values())

    # def removeExtraStatStrength(self,tag:str):
    #     del self.extra_strength[tag]
    #     self.extra_strength_sum = sum(self.extra_strength.values())

    # def removeExtraStatEnergy(self,tag:str):
    #     del self.extra_energy[tag]
    #     self.extra_energy_sum = sum(self.extra_energy.values())
    
    # def removeExtraStatDefense(self,tag:str):
    #     del self.extra_defense[tag]
    #     self.extra_defense_sum = sum(self.extra_defense.values())
     
    # ### GET STATS ###

    # def getTotalSpeed(self):
    #     return self.speed + self.extra_speed_sum
    
    # def getTotalTotalHealth(self):
    #     return self.total_health + self.extra_total_health_sum
    
    # def getTotalRegen(self):
    #     return self.regen_multiplier + self.extra_speed_sum
    
    # def getTotalStrength(self):
    #     return self.strength + self.extra_strength_sum
    
    
    # @property
    # def selected_item(self) -> Optional['Application.Game.Items.Item']:
    #     if self.inventory.spaces == 0 :return None
    #     return self.inventory.inventory[0]

    # def depleteEnergy(self,action):
    #     assert action in self.actions, f'{self.typeid} has tried to do actions: {action}, which is not in its list of actions!'
    #     self.energy -= Settings.ACTION_ENERGY_CONSUMPTION[action]
    #     if self.energy < 0:
    #         self.take_damage(-self.energy,INTERNAL_DAMAGE,None)
    #         self.energy = 0
        
    # def canDoAction(self,action):
    #     '''Returns if self HAS ENOUGH ENERGY to do the action, keep in mind that the action can still be taken if this returns False, just with consequences...'''
    #     assert action in self.actions,  f'{self.typeid} has tried to do actions: {action}, which is not in its list of actions!'
    #     return self.energy >= Settings.ACTION_ENERGY_CONSUMPTION[action]

    # def get_entities_seen(self):
    #     for entity in collide_entities(self.vision_collider):
    #         if entity is not self and (entity.pos - self.pos).magnitude_squared() <= self.vision_squared and can_see_each_other(self,entity):
    #             yield entity    

    # def onDeath(self):
    #     if super().onDeath():
    #         for i in range(10):
    #             Particles.spawn(CSurface.inferOffset(Textures.particles_opaque['white'],self.pos + Vector2.random()/5),1.0,Vector2.random()/2,slows_coef=0)
    #         Particles.spawn(self.animation.csurface.copy(),1.0)
    #         return True
    #     return False

    # def set_state(self,number:int):
    #     '''Returns False if failed.
    #     Reasons for failing:
    #         * The Entity is already in that state'''
    #     if self.state is self.states[number]: return False
    #     self.state = self.states[number]
    #     self.animation.set_state(self.state)

    # def set_regen_time(self,speed:float) -> None:
    #     self.regen_time = speed
    #     if self.time_to_regen > speed:
    #         self.time_to_regen = speed

    def update(self): ...

    # def get_damage_resisted(self,damage:int,type:str) -> int:
    #     '''Returns damage resisted'''
    #     if type is INTERNAL_DAMAGE: return 0
    #     defense:int = self.defense + self.inventory.added_def
    #     damage_reduction = damage * defense/ (defense+100) 
    #     return damage_reduction.__trunc__()
    
    # def take_damage(self,damage:int,type:str,appearance:Appearance|None = None) -> None:
            
    #     if self.time_til_vulnerable < 0 or type is INTERNAL_DAMAGE: 
    #         damage -= self.get_damage_resisted(damage,type)
    #         if damage == 0:
    #             return
    #         Particles.spawn_hit_particles(self.pos,.5)
    #         self.health -= damage
    #         print('taking damage',damage,'now health is',self.health)
    #         if self.health <= 0:
    #             self.onDeath()
    
    # def get_energy_multiplier(self) -> float:
    #     return (self.energy/self.stats['energy'] + 1)/2

    # def get_attack_damage(self) -> int:
    #     '''Returns final attack damage'''
    #     #get total damage stat
    #     damage =  self.getTotalStrength() # start with strength stat
    #     damage *= 1.0 + self.strength / 100 * self.get_energy_multiplier()
    #     return damage.__trunc__()

    # def get_attack_type(self) -> str:
    #     return PHYSICAL_DAMAGE
    
    # def natural_regen(self):
    #     if self.health != self.total_health and self.time_til_vulnerable < -10: # if 10 seconds have passed since we have been dealth damage that resets our invulnerability timer
    #         self.time_to_regen -= Time.deltaTime
    #         if self.time_to_regen < 0:
    #             self.time_to_regen = self.regen_time
    #             self.health += max(1,(self.total_health/100 *  self.regen_multiplier * self.get_energy_multiplier()).__trunc__())
    #             if self.health > self.total_health:
    #                 self.health = self.total_health
    #             print(self.health)

    # def collect_items(self):
    #     for item in collide_entities_in_range_species(self.pos,self.pickup_range,'item'): # type: ignore
    #         item:ItemWrapper
    #         if item.pickup_time < 0 :
    #             i = self.inventory.fitItem(item.item) #this will never add the same object to both hotbar and inventory becasue the or will only try to add to inventory if the item couldn't be added to the hotbar
    #             if i is None:
    #                 item.onDeath()

