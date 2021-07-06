# Creature class module

import random
import status

# Initialise variables for hit locations
hit_location_names = ['Head','Off Hand','Body','Favoured Hand','Off Leg','Favoured Leg']
base_hit_location_weightings = [4,1,4,6,1,4]

# Initialise core statuses
status_prone = status.Status('Prone', 0.75, [1.5,2,1,1,1,0.25])
status_off_hand = status.Status('Using Off hand', 0.75, [1,1,1,1,1,1])
status_disarmed = status.Status('Disarmed', 0, [1,1,1,1,1,1])

# Setup a class for creatures that can fight
class Creature:
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

    def check_use_ability(self):
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

class Global(Creature):
    'Class which defines creatures with global hits'
    name_hit_list = ['Global']
    base_chance_hit_list = [1]
    hit_num_list = [1]

    def check_incapacitated(self):
        'Return 1 if the creature is incapacitated and incapable of fighting and 0 otherwise'
        # Global creatures are incapacitated if their hits drop to zero
        if self.currhits[0] <= 0:
            return 1
        else:
            return 0

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
        # Store the pre-damage hits for status checks later on
        _oldhits = list.copy(self.currhits)
        # For locational creatures we need to check if the location is a limb and if it is already destroyed
        if hit_location_num not in [0,2] and self.currhits[hit_location_num] <= -3:
            # If so redirect damage to body
            self.currhits[2] -= damage
        # Otherwise apply damage as normal
        else:
            self.currhits[hit_location_num] -= damage
        # Applying wounding based statuses
        # "Prone" status - Apply when either leg is hit and drops to zero
        if hit_location_num in [4,5] and _oldhits[hit_location_num] > 0 and self.currhits[hit_location_num] <= 0:
            self.apply_status(status_prone,-1)
        # When Favoured Hand is hit and drops below zero apply "Using Off Hand" permanently and "Disarmed" for one round
        if hit_location_num == 1 and _oldhits[hit_location_num] >=0 and self.currhits[hit_location_num] <= 0:
            self.apply_status(status_off_hand,-1)
            self.apply_status(status_disarmed,1) 

    def check_incapacitated(self):
        'Return 1 if the creature is incapacitated and incapable of fighting and 0 otherwise'
        # Locational creatures are incapacitated if any critical location, or all arm locations, drop to zero
        if self.currhits[0] <= 0 or self.currhits[2] <= 0:
            return 1
        elif self.currhits[1] <= 0 and self.currhits[3] <= 0:
            return 1
        else:
            return 0

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
    def check_use_ability(self):
        'Return 1 and the ability they will use if creature will use a special ability this round, else return 0 and None'
        # Now that we have abilities as objects which are then listed in the creatures abilities we can just loop over them to check which to use
        # This means we are assuming the list of abilities is priority ranked, which makes sense and lets us adjust "strategies"
        # This only really supports simple, fast abilities right now - higher level spells need to be able to be interrupted, and miracles take time to cast
        for ability in self.abilities:
            curr, max = (ability.resource_activate + '_points', ability.resource_activate + '_points_max')
            # If not enough resource, do not use ability - This won't support zero cost abilities as implmented, because of a divide by zero issue
            if getattr(self, curr) < ability.resource_cost:
                continue
            elif getattr(self, curr)/getattr(self, max) > (sum(self.currhits)/sum(self.maxhits)):
                return ability
        return None

    # TT Characters need their own damage_creature method which accounts for sources of armour
    def damage_creature(self,hit_location_num,damage):
        'Apply damage to a location on a creature based on the appropriate logic for its type'
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