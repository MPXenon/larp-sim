# Module containing various versions of the fight logic
import random
from sys import exit

# Base chance to trade blows instead of either party getting a clean hit when their skill is equal
chance_trade_base = 0.5 

# Initialise hit location names for logging
hit_location_names = ['Head','Off Hand','Body','Favoured Hand','Off Leg','Favoured Leg']

def log_ability_use(source,target,ability,log_mode):
    'Function to record ability usage in text log'
    if log_mode == 2:
        print(source.name,'used',ability.name,'on',target.name)
        # If resource spend then show remaining
        if ability.resource_activate != None:
            print(source.name,'has',getattr(source,ability.resource_activate + '_points'),'of',getattr(source,ability.resource_activate + '_points_max'),ability.resource_activate,'remaining')

def log_hit(source,target,location_number,location_name,damage,log_mode):
    if log_mode == 2:
        print(source.name, 'hits the', location_name, 'of', target.name, 'for', damage, 'damage')
        print(target.name, location_name, 'has', target.currhits[location_number], 'of', target.maxhits[location_number],'hits remaining')

def use_ability(source,target,ability,log_mode,hit_location_num=None):
    'Function for source creature to use ability in fight with target'
    # Spend source creature resource if applicable
    if ability.resource_activate != None:
        setattr(source,ability.resource_activate + '_points',getattr(source,ability.resource_activate + '_points') - ability.resource_cost)
    # If ability is a status granting ability set status on appropriate ability target
    if ability.type == 'abilitygrantstatus':
        if 'hostile' in ability.target:
            target.apply_status(ability.associated_status,ability.associated_status_duration)
            log_ability_use(source,target,ability,log_mode)
        elif 'self' in ability.target:
            source.apply_status(ability.associated_status,ability.associated_status_duration)
            log_ability_use(source,source,ability,log_mode)
    # If ability is direct damage and can target hostile then deal direct damage to the target
    if ability.type == 'abilitydamagedirect' and 'hostile' in ability.target:
        target.damage_creature_direct(ability.damage)
        log_ability_use(source,target,ability,log_mode)
        log_hit(source,target,2,hit_location_names[2],ability.damage,log_mode)
    # If ability is heal creature and can target self then heal source
    if ability.type == 'abilityhealcreature' and 'self' in ability.target:
        source.heal_creature(ability.healing)
        log_ability_use(source,source,ability,log_mode)
    # If ability is affect creature - currently self only
    if ability.type == 'abilityaffectcreature' and 'self' in ability.target:
        source.change_attribute_creature(ability.attribute_target,ability.attribute_change_mode,ability.attribute_mod)
        log_ability_use(source,source,ability,log_mode)
    # If ability replaces damage then damage the target in the same location as the hit
    if ability.type == 'abilitydamagelocation' and 'hostile' in ability.target:
        target.damage_creature(hit_location_num,ability.damage)
        log_ability_use(source,target,ability,log_mode)
        log_hit(source,target,hit_location_num,hit_location_names[hit_location_num],ability.damage,log_mode)

def use_ability_fast(source,target,ability,log_mode):
    'Function for source creature to use selected ability in fight with target if it is a valid fast ability'
    if ability == None:
        return
    elif ability.speed == 'fast':
        use_ability(source,target,ability,log_mode)

def use_ability_slow(source,target,ability,source_was_hit,log_mode):
    'Function for source creature to use selected ability in fight with target if it is a valid slow ability'
    if ability == None:
        return
    elif (ability.speed == 'interruptible' and source_was_hit == 0) or (ability.speed == 'uninterruptible' and source.check_incapacitated() == 0):
        use_ability(source,target,ability,log_mode)

def trigger_charges(source,target,hit_location_num,log_mode):
    'Function for any stored charges on source creature to be discharged and their abilities activated'
    # Create a list of any abilities triggered from stored charges on the source creature
    discharge_abil_list = [stat.charged_ability for stat in source.status if stat.type == 'statuscharge']
    # Loop through this list triggering the charged abilities
    for abil in discharge_abil_list:
        use_ability(source,target,abil,log_mode,hit_location_num)
    # Identify statuses of spent charges to be removed
    deletelist = [x for x in range(len(source.status)) if source.status[x].type == 'statuscharge']
    # Loop backwards over the deletelist and remove expired statuses
    for index in sorted(deletelist,reverse=1):        
        del source.status[index]
        del source.status_durations[index]

def run_solo_encounter(fighter_a,fighter_b,log_mode):
    'Run a solo encounter between fighter_a and fighter_b and return 0 for a draw, 1 for a fighter_a win and 2 for a fighter_b win'
    # Initialize round counter
    round_count = 0
    
    # Round Loops
    while 1:
        # Increment and Print Round tracker 
        round_count += 1
        if log_mode == 2: 
            print('Round', round_count, ":")

        # Update Statuses
        fighter_a.update_status()
        fighter_b.update_status()

        # Reset hit check variables
        fighter_a_was_hit,fighter_b_was_hit = 0,0

        # Check if the parties will use any abilities and return the ones they will use
        fighter_a_use_ability,fighter_b_use_ability = fighter_a.check_use_ability(fighter_b),fighter_b.check_use_ability(fighter_a)

        # Implement logic for using fast abilities - need to do this before we calculate fighter ratings as it can modify them
        # Note : "Combo's" like Glimmer + Enhancement would need to implemented as their own "Ability" - since only one ability is ever used per round
        use_ability_fast(fighter_a,fighter_b,fighter_a_use_ability,log_mode)
        use_ability_fast(fighter_b,fighter_a,fighter_b_use_ability,log_mode)

        # Store the fighter ratings as temp variables to avoid repetition of the getter logic
        _fighter_a_rating,_fighter_b_rating = fighter_a.rating,fighter_b.rating
        
        # Exception for both fighters having a rating of Zero - skip the round
        if _fighter_a_rating == 0 and _fighter_b_rating == 0:
            continue

        # Calculate the variables for working out round winner  - scaled by the skill gap of the creatures
        chance_trade = min(_fighter_a_rating,_fighter_b_rating)/max(_fighter_a_rating,_fighter_b_rating)*chance_trade_base
        fighter_a_hit_chance = _fighter_a_rating*((1-chance_trade)/(_fighter_a_rating+_fighter_b_rating))

        # Get all the random numbers required
        round_rand_hit = random.random()

        # Determine potential hit locations
        hit_location_num_a = fighter_a.determine_hit_location()
        hit_location_num_b = fighter_b.determine_hit_location()
        if type(fighter_a).__name__ in ['Global']:
            hit_location_name_a = 'Global'
        else:
            hit_location_name_a = hit_location_names[hit_location_num_a]
        if type(fighter_b).__name__ in ['Global']:
            hit_location_name_b = 'Global'
        else:
            hit_location_name_b = hit_location_names[hit_location_num_b]
        
        # Perform the hit logic and launch any charge abilities
        if 0 <= round_rand_hit < fighter_a_hit_chance :
            fighter_b.damage_creature(hit_location_num_b,fighter_a.damage)
            fighter_b_was_hit = 1
            log_hit(fighter_a,fighter_b,hit_location_num_b,hit_location_name_b,fighter_a.damage,log_mode)
            trigger_charges(fighter_a,fighter_b,hit_location_num_b,log_mode)
        elif fighter_a_hit_chance <= round_rand_hit < (fighter_a_hit_chance+chance_trade) :
            fighter_b.damage_creature(hit_location_num_b,fighter_a.damage)
            fighter_a.damage_creature(hit_location_num_a,fighter_b.damage)
            fighter_a_was_hit,fighter_b_was_hit = 1,1
            log_hit(fighter_a,fighter_b,hit_location_num_b,hit_location_name_b,fighter_a.damage,log_mode)
            log_hit(fighter_b,fighter_a,hit_location_num_a,hit_location_name_a,fighter_b.damage,log_mode)
            trigger_charges(fighter_a,fighter_b,hit_location_num_b,log_mode)
            trigger_charges(fighter_b,fighter_a,hit_location_num_a,log_mode)
        elif (fighter_a_hit_chance+chance_trade) <= round_rand_hit <= 1 :
            fighter_a.damage_creature(hit_location_num_a,fighter_b.damage)
            fighter_a_was_hit = 1
            log_hit(fighter_b,fighter_a,hit_location_num_a,hit_location_name_a,fighter_b.damage,log_mode)
            trigger_charges(fighter_b,fighter_a,hit_location_num_a,log_mode)
        else :
            print('Error: Unspecified combat round outcome')
            exit()

        # Perform end of round status checks
        x = fighter_a.check_incapacitated()
        y = fighter_b.check_incapacitated()

        # Implement logic for using interruptible (if not hit while casting) and uniterruptible abilities
        use_ability_slow(fighter_a,fighter_b,fighter_a_use_ability,fighter_a_was_hit,log_mode)
        use_ability_slow(fighter_b,fighter_a,fighter_b_use_ability,fighter_b_was_hit,log_mode)

        # Output Fight Result
        if x == 1 and y == 1:
            return 0
        elif y == 1:
            return 1
        elif x == 1:

            return 2
