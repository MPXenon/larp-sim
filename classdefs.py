import random
import jsonpickle

# Setup a class for so everything to have a string representation
class FileItem():
    def __str__(self):
        return jsonpickle.encode(self)

# Setup a class for statuses
class Status(FileItem):
    'Class that defines statuses which affect combat'
    type = 'statusbasic'
    def __init__(self,name,status_rating_multi=1,status_hit_multi=[1,1,1,1,1,1],status_damage_mod=0,status_damage_multi=1):
        self.name,self.status_rating_multi,self.status_hit_multi = name,status_rating_multi,status_hit_multi
        self.status_damage_mod,self.status_damage_multi = status_damage_mod,status_damage_multi

# Setup a subclass for "Charged" ability statuses
class StatusCharged(Status):
    'Class that defines statuses which grant charges of abilities'
    type = 'statuscharge'
    def __init__(self,name,charged_ability,status_rating_multi=1,status_hit_multi=[1,1,1,1,1,1],status_damage_mod=0,status_damage_multi=1):
        super().__init__(name,status_rating_multi,status_hit_multi,status_damage_mod,status_damage_multi)
        self.charged_ability = charged_ability

# Setup a class for weapons
class Weapon(FileItem):
    'Class that defines weapons which affect combat'
    def __init__(self,name,weapon_rating_multi,weapon_hit_multi):
        self.name,self.weapon_rating_multi,self.weapon_hit_multi = name,weapon_rating_multi,weapon_hit_multi

# Setup a class for special abilities
class Ability(FileItem):
    'Base Class that defines abilities which affect combat'
    type = None
    def __init__(self,name,target,speed,resource_activate,resource_cost):
        self.name,self.target,self.speed,self.resource_activate,self.resource_cost = name,target,speed,resource_activate,resource_cost

class AbilityGrantStatus(Ability):
    'Class that defines abilities which apply a status effect'
    type = 'abilitygrantstatus'
    def __init__(self,name,target,speed,resource_activate,resource_cost,associated_status,associated_status_duration):
        super().__init__(name,target,speed,resource_activate,resource_cost)
        self.associated_status,self.associated_status_duration = associated_status,associated_status_duration

class AbilityDamageDirect(Ability):
    'Class that defines abilities which damage directly damage a creature'
    type = 'abilitydamagedirect'
    # This is the TT equivalent of a "THREE" as opposed to a "TRIPLE"
    # Note : Damage types not implemented
    def __init__(self,name,target,speed,resource_activate,resource_cost,damage):
        super().__init__(name,target,speed,resource_activate,resource_cost)
        self.damage = damage
    
class AbilityDamageLocation(Ability):
    'Class that defines abilities which deal damage which hits the struck location'
    type = 'abilitydamagelocation'
    # This exists for the purpose of charge abilities
    # Note : Damage types not implemented
    def __init__(self,name,target,speed,resource_activate,resource_cost,damage):
        super().__init__(name,target,speed,resource_activate,resource_cost)
        self.damage = damage

class AbilityHealCreature(Ability):
    'Class that defines abilities which heal creatures'
    type = 'abilityhealcreature'
    # Note : This only supports immediate numerical healing abilities, it doesn't support "heal sufficient" or "lay on hands" miracles
    def __init__(self,name,target,speed,resource_activate,resource_cost,healing):
        super().__init__(name,target,speed,resource_activate,resource_cost)
        self.healing = healing

class AbilityAffectCreature(Ability):
    'Class that defines abilities which directly modify certain creature attributes'
    # Note : This functions in two "modes"; abilities which set the value, and abilities which modify the value
    # Note : Only designed to work with resources or global armour (i.e "instantaneous changes") - to modify damage or rating use a status
    type = 'abilityaffectcreature'
    def __init__(self,name,target,speed,resource_activate,resource_cost,attribute_target,attribute_mod,attribute_change_mode):
        super().__init__(name,target,speed,resource_activate,resource_cost)
        self.attribute_target,self.attribute_mod,self.attribute_change_mode = attribute_target,attribute_mod,attribute_change_mode

# Setup Creature Classes
# Initialise variables for hit locations
hit_location_names = ['Head','Off Hand','Body','Favoured Hand','Off Leg','Favoured Leg']
base_hit_location_weightings = [4,1,4,6,1,4]

# Initialise healing location priority - lets say the priority order is Head, Body, Favoured Hand, Favoured Leg, Off Leg, Off Hand
heal_loc_priority = (0,2,3,5,4,1)

# Initialise core statuses
status_prone = Status('Prone', 0.75, [1.5,2,1,1,1,0.25])
status_off_hand = Status('Using Off hand', 0.75, [1,1,1,1,1,1])
status_disarmed = Status('Disarmed', 0, [1,1,1,1,1,1])

# Setup a class for creatures that can fight
class Creature(FileItem):
    'Class that defines all combat capable creatures'

    name_hit_list,base_chance_hit_list = [],[]

    def __init__(self,name,base_rating,maxhits,base_damage,weapons=[]):
        self.name,self.base_rating,self.maxhits,self.base_damage = name,base_rating,maxhits,base_damage
        self.status,self.status_durations,self.currhits,self.weapons = [],[],list.copy(self.maxhits),list.copy(weapons)

    def get_chance_hit_list(self):
        _chance_hit_list = list.copy(self.base_chance_hit_list)
        return _chance_hit_list

    def get_hit_num_list(self):
        return []

    def get_rating(self):
        _rating = self.base_rating
        # Check for statuses and weapons that impact rating
        for x in self.status:
            _rating = _rating*x.status_rating_multi
        for y in self.weapons:
            _rating = _rating*y.weapon_rating_multi
        return _rating

    def get_damage(self):
        _damage = self.base_damage
        # Check for statuses that impact damage
        # Note : We have chosen to apply modifier before multiplier - this is consistent with how things work in DUTT
        for x in self.status:
            _damage += x.status_damage_mod
            _damage = _damage*x.status_damage_multi
        return _damage
    
    chance_hit_list = property(get_chance_hit_list)
    hit_num_list = property(get_hit_num_list)
    rating = property(get_rating)
    damage = property(get_damage)

    def initialize_creature(self):
        'Reset a creatures perameters to the base state'
        self.status,self.status_durations,self.currhits = [],[],list.copy(self.maxhits)

    def check_use_ability(self,target):
        'Check if creature will use a special ability this round and which they will use'
        return None

    def determine_hit_location(self):
        'Return a hit location number using the creatures location weightings'
        # Setup temporary variables for random number and repetition avoidance
        rand_no_location = random.random()
        _hit_num_list = list.copy(self.hit_num_list)
        # Handle the case of Global hits monsters
        if len(_hit_num_list) == 1:
            hit_location_num = 0
        # Otherwise use the location list
        else:
            for x in range(len(_hit_num_list)):
                if _hit_num_list[x] <= rand_no_location <= _hit_num_list[x+1]:
                    hit_location_num = x
        return hit_location_num
    
    def damage_creature(self,hit_location_num,damage):
        'Apply damage to a location on a creature based on the appropriate logic for its type'
        # Don't apply damage if it would be zero or less
        if damage >= 0:
            self.currhits[hit_location_num] -= damage

    def apply_status(self,newstatus,newstatus_duration):
        'Apply a status to a creature; -1 for permanent durations'
        # No duplicate statuses allowed so do a check
        if newstatus not in self.status:
            list.append(self.status,newstatus)
            list.append(self.status_durations,newstatus_duration)
        else:
             return

    def update_status(self):
        'Update the status of a creature at the start of a new round'
        # Initialise a blank list of statuses to delete
        deletelist = []
        # Loop over statuses
        for x in range(len(self.status_durations)):
            # Identify statuses with no remaining duration which are to be removed
            if self.status_durations[x] == 0:
                deletelist.append(x)
            # If a status has a positive duration reduce it by one
            if self.status_durations[x] > 0:
                self.status_durations[x] -= 1
        # Loop backwards over the deletelist and remove expired statuses
        for index in sorted(deletelist,reverse=1):        
            del self.status[index]
            del self.status_durations[index]          

# Should rename this class to something less likely to cause python issues
class Global(Creature):
    'Class which defines creatures with global hits'
    name_hit_list = ['Global']
    base_chance_hit_list = [1]
    hit_num_list = [1]

    def damage_creature_direct(self,damage):
        'Apply direct damage to a creature based on the appropriate logic for its type'
        if damage >= 0:
            self.currhits[0] -= damage

    def check_incapacitated(self):
        'Return 1 if the creature is incapacitated and incapable of fighting and 0 otherwise'
        # Global creatures are incapacitated if their hits drop to zero
        if self.currhits[0] <= 0:
            return 1
        else:
            return 0

    def heal_creature(self,healing):
        'Apply healing to creature in a (somewhat) logical fashion'
        # Global healing is simple, just don't let it overflow the maxhits
        self.currhits[0] = min((self.currhits[0] + healing, self.maxhits[0]))

    def get_healable_damage(self):
        'Return the total ammount of damage which can still be healed (i.e to non-destroyed locations) the creature has taken'
        healable_damage = self.maxhits[0] - self.currhits[0]
        return healable_damage

class Locational(Creature):
    'Class which defines creatures with locational hits'
    name_hit_list = hit_location_names
    base_chance_hit_list = base_hit_location_weightings
    
    def get_chance_hit_list(self):
        _chance_hit_list = list.copy(self.base_chance_hit_list)
        # Check for weapons and statuses that impact hit list
        for x in self.weapons:
            if (self.currhits[1] > 0 and self.currhits[3] > 0):
                _chance_hit_list = [a * b for a, b in zip(_chance_hit_list,x.weapon_hit_multi)]
        # Status implementation
        for y in self.status:
            _chance_hit_list = [a * b for a, b in zip(_chance_hit_list,y.status_hit_multi)]
            # Specific case for using off hand
            if y.name == 'Using Off Hand':
                # Swap on and off arms and legs
                _chance_hit_list[1],_chance_hit_list[3] = _chance_hit_list[3],_chance_hit_list[1]
                _chance_hit_list[4],_chance_hit_list[5] = _chance_hit_list[5],_chance_hit_list[4]        
        return _chance_hit_list

    def get_hit_num_list(self):
        # Use a temporary copy of the chance_hit_list to avoid repetition of it's getter
        _chance_hit_list = list.copy(self.chance_hit_list)
        # Scale the chance hit list to be a percentage to deal with aribtrarily sized input weightings
        _chance_hit_percentage = [x/sum(_chance_hit_list) for x in _chance_hit_list]
        return [0,sum(_chance_hit_percentage[:1]),sum(_chance_hit_percentage[:2]),sum(_chance_hit_percentage[:3]),sum(_chance_hit_percentage[:4]),sum(_chance_hit_percentage[:5]),sum(_chance_hit_percentage)]

    def get_rating(self):
        _rating = self.base_rating
        # Check for statuses and weapons that impact rating
        for x in self.status:
            _rating = _rating*x.status_rating_multi
        # For a loctional hits creature both hands must be uninjured for the shield or off hand weapon to function
        for y in self.weapons:
            if self.currhits[1] > 0 and self.currhits[3] > 0:
                _rating = _rating*y.weapon_rating_multi
        return _rating

    # We *MUST* restate properties whose functions have changed, else the parent ones will be used
    chance_hit_list = property(get_chance_hit_list)
    hit_num_list = property(get_hit_num_list)
    rating = property(get_rating)
    
    def damage_creature(self,hit_location_num,damage):
        'Apply damage to a location on a creature based on the appropriate logic for its type'
        if damage >= 0:
            # Store the pre-damage hits for status checks later on
            _oldhits = list.copy(self.currhits)
            # For locational creatures we need to check if the location is a limb and if it is already destroyed
            if hit_location_num not in [0,2] and self.currhits[hit_location_num] <= -3:
                # If so redirect damage to body and prevent hits going below -3
                self.currhits[2] = max((self.currhits[2] - damage),-3)
            # Otherwise apply damage as normal
            else:
                self.currhits[hit_location_num] = max((self.currhits[hit_location_num] - damage),-3)
            # Applying wounding based statuses
            # "Prone" status - Apply when either leg is hit and drops to zero
            if hit_location_num in [4,5] and _oldhits[hit_location_num] > 0 and self.currhits[hit_location_num] <= 0:
                self.apply_status(status_prone,-1)
            # When Favoured Hand is hit and drops below zero apply "Using Off Hand" permanently and "Disarmed" for one round
            if hit_location_num == 1 and _oldhits[hit_location_num] >=0 and self.currhits[hit_location_num] <= 0:
                self.apply_status(status_off_hand,-1)
                self.apply_status(status_disarmed,1) 

    def damage_creature_direct(self,damage):
        'Apply direct damage to a creature based on the appropriate logic for its type'
        # On a locational creature direct damage goes straight to the body
        if damage >= 0:
            self.damage_creature(2,damage)

    def check_incapacitated(self):
        'Return 1 if the creature is incapacitated and incapable of fighting and 0 otherwise'
        # Locational creatures are incapacitated if any critical location, or all arm locations, drop to zero
        if self.currhits[0] <= 0 or self.currhits[2] <= 0:
            return 1
        elif self.currhits[1] <= 0 and self.currhits[3] <= 0:
            return 1
        else:
            return 0

    # Identify the ammount of damage a character has taken which can be healed
    def get_healable_damage(self):
        'Return the total ammount of damage which can still be healed (i.e to non-destroyed locations) the creature has taken'
        healable_damage = 0
        for x in range(len(self.maxhits)):
            if self.currhits[x] > -3 and self.currhits[x] < self.maxhits[x]:
                healable_damage += self.maxhits[x] - self.currhits[x]
        return healable_damage
    
    def heal_creature(self,healing):
        'Apply healing to creature in a (somewhat) logical fashion; prioritising the most wounded non-destroyed location and then a preset location order'
        # Loop through assigning healing points one at a time  
        for x in range(healing):
            # Create a list of the still active locations and use that to find the "real minimum" once destroyed locations excluded
            real_minhits = min(x for x in self.currhits if x > -3)
            # Find the hit location numbers of any locations with the minimum number of current hits
            minhit_location_list = [index for index,val in enumerate(self.currhits) if val == real_minhits]
            # Loop through the healing priority list looking for locations that are also in the list of locations on minimum hits
            for y in heal_loc_priority:
                if y in minhit_location_list:
                    # If the location is not on max already heal the location for one hit and reduce the number of remaining healing points by one, then break to the outer loop
                    if self.currhits[y] < self.maxhits[y]:
                        self.currhits[y] += 1
                        healing -= 1
                        break
            # If we get to the end of the healing priority list without having healed anything heal any non-destroyed location on less than maximum in priority order
            else:   
                for z in heal_loc_priority:
                    if self.currhits[y] > -3 and self.currhits [y] < self.maxhits[y]:
                        self.currhits[y] += 1
                        healing -= 1
                        break
                else:
                    # If after all that we still haven't used the healing the target is fully healed and we can return
                    return
            

class TreasureTrapPC(Locational):
    'Class for player characters built using the DUTT Ruleset'
    # Adds TT offense and defence into the creature
    def __init__(self,name,base_rating,maxhits,base_damage,weapons=[],abilities=[],loc_armour=[0,0,0,0,0,0],
                glob_dac=0,glob_spirit_arm=0,glob_magic_arm=0,mana_points=0,spirit_points=0,alchemy_points=0,herb_points=0):
        self.name,self.base_rating,self.maxhits,self.base_damage = name,base_rating,maxhits,base_damage
        self.status,self.status_durations,self.currhits,self.weapons,self.abilities = [],[],list.copy(self.maxhits),list.copy(weapons),list.copy(abilities)
        self.loc_armour_max,self.glob_dac_max,self.glob_spirit_arm_max,self.glob_magic_arm_max = list.copy(loc_armour),glob_dac,glob_spirit_arm,glob_magic_arm
        self.loc_armour,self.glob_dac,self.glob_spirit_arm,self.glob_magic_arm = list.copy(loc_armour),glob_dac,glob_spirit_arm,glob_magic_arm
        self.mana_points_max,self.spirit_points_max,self.alchemy_points_max,self.herb_points_max  = mana_points,spirit_points,alchemy_points,herb_points
        self.mana_points,self.spirit_points,self.alchemy_points,self.herb_points = mana_points,spirit_points,alchemy_points,herb_points

    # TT Characters need an extended initialisation method to reset armour and resources
    def initialize_creature(self):
        'Reset a creatures perameters to the base state'
        self.status,self.status_durations,self.currhits = [],[],list.copy(self.maxhits)
        self.loc_armour,self.glob_dac,self.glob_spirit_arm,self.glob_magic_arm = list.copy(self.loc_armour_max),self.glob_dac_max,self.glob_spirit_arm_max,self.glob_magic_arm_max
        self.mana_points,self.spirit_points,self.alchemy_points,self.herb_points = self.mana_points_max,self.spirit_points_max,self.alchemy_points_max,self.herb_points_max

    # TT Characters can use special abilities if they have enough resources, need a check to see which they will use them in a combat round
    def check_use_ability(self,target):
        'Return 1 and the ability they will use if creature will use a special ability this round, else return 0 and None'
        # Now that we have abilities as objects which are then listed in the creatures abilities we can just loop over them to check which to use
        # This means we are assuming the list of abilities is priority ranked, which makes sense and lets us adjust "strategies"
        for ability in self.abilities:
            curr, max = (ability.resource_activate + '_points', ability.resource_activate + '_points_max')
            # If not enough resource, do not use ability - This won't support zero cost abilities as implmented, because of a divide by zero issue
            if getattr(self, curr) < ability.resource_cost:
                continue
            # Trigger resource usage when proportion of total hits, or hits on an individual critical location drop below proportion of remaining resource, or when an individual critical location drops to one
            # Note : In exceptional cases the total of currhits can go negative, at which point no abilities will be spammed continually - not nessecarily wrong though!
            elif getattr(self, curr)/getattr(self, max) > (sum(self.currhits)/sum(self.maxhits)) \
                 or getattr(self, curr)/getattr(self, max) >= self.currhits[0]/self.maxhits[0]   \
                 or getattr(self, curr)/getattr(self, max) >= self.currhits[2]/self.maxhits[2]   \
                 or self.currhits[0] == 1 or self.currhits[2] == 1:
                # If the ability is healing to be used on self then skip over if any healing will be "wasted" because it exceeds damage which can be healed
                # WARNING : This will be further complicated once multi party fights mean friendlies can be healed or when we introduce "heal sufficient"
                if ability.type == 'abilityhealcreature' and 'self' in ability.target and self.get_healable_damage() < ability.healing:
                    continue
                # If the ability is an attribute setter then skip over if it would be wasted or redundant
                # WARNING : Simple logic for now, don't recast if there's any of the attribute left
                elif ability.type == 'abilityaffectcreature' and 'self' in ability.target and getattr(self,ability.attribute_target) > 0:
                    continue
                # If the ability is a status ability don't cast it again if it would cause a duplicate status and thus have no effect
                # WARNING : There is a rare edge case getting through all these checks that I need to find - need to do a massive data dump to ID
                # Note : Status checks will only check for exact matches, not just "similar" statuses - so need to be consistent with statuses which can come from multiple sources
                elif ability.type == 'abilitygrantstatus' and 'self' in ability.target and (ability.associated_status in self.status):
                    continue
                elif ability.type == 'abilitygrantstatus' and 'hostile' in ability.target and (ability.associated_status in target.status):
                    continue
                # If the ability is a charge ability don't cast it if already holding a charge
                elif ability.associated_status.type == 'statuscharge' and 'statuscharge' in [stat.type for stat in self.status if stat.type == 'statuscharge']:
                    continue  
                # If the ability is a charge ability don't cast it if the status of the discharged ability from the charged status is already on the target
                # ERROR : Issue with non status charge abilities
                elif ability.associated_status.type == 'statuscharge' and (getattr(ability.associated_status.charged_ability,'associated_status','MISSING') in target.status):
                    continue
                else:
                    return ability
                
        return None

    def get_resource_spent(self,resource_name):
        'Return the number of the resource_name spent'
        curr, max = resource_name + '_points', resource_name + '_points_max'
        resource_spent = getattr(self,max) - getattr(self,curr)
        return resource_spent

    # TT Characters need their own damage_creature method which accounts for sources of armour
    def damage_creature(self,hit_location_num,damage):
        'Apply damage to a location on a creature based on the appropriate logic for its type'
        if damage >= 0:
            # Note : Not official TT rules, but let's establish an order of operations that goes DAC, Spirit, Magic, Physical
            # Note : Damage types are not yet implemented
            # Loop over the armour attributes as long as there is still damage to assign
            for elm in ['glob_dac','glob_spirit_arm','glob_magic_arm']:
                x = getattr(self, elm)
                # If no armour of this type go to next one in the list
                if x == 0:
                    continue
                # Establish if the damage is completely negated by this armour and if so reduce armour and return
                elif damage <= x:
                    setattr(self,elm,x-damage)
                    return
                # Otherwise calculate the remaining damage and reduce armour to zero
                else:
                    damage -= x
                    setattr(self,elm,0)
            # We do the physical locational armour seperately because the attribute takes the form of a list
            if self.loc_armour[hit_location_num] > 0:
                if damage <= self.loc_armour[hit_location_num]:
                    self.loc_armour[hit_location_num] -= damage
                    return
                else:
                    damage -= self.loc_armour[hit_location_num]
                    self.loc_armour[hit_location_num] = 0
                    
            # Run the rest of the damage logic for a locational with any remaining damage
            super().damage_creature(hit_location_num,damage)
    
    # TT Characters need a method which allows non-hit point attributes to be changed, such as adding locational armour
    def change_attribute_creature(self,attribute_target,type,modnum):
        'Modify a non-hit point attribute'    
        if type == 'set':
            setattr(self,attribute_target,modnum)
        if type == 'mod':
            setattr(self,attribute_target,getattr(self,attribute_target)+modnum)
