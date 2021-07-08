# Module containing various versions of the fight logic
import random
from sys import exit

# Base chance to trade blows instead of either party getting a clean hit when their skill is equal
chance_trade_base = 0.5 

# Initialise hit location names for logging
hit_location_names = ['Head','Off Hand','Body','Favoured Hand','Off Leg','Favoured Leg']

def use_ability(source,target,ability,log_mode):
    'Function for source creature to use ability in fight with target'
    # Spend source creature resource
    source_resource_spend = ability.resource_activate + '_points'
    source_resource_max = ability.resource_activate + '_points_max'
    setattr(source,source_resource_spend,getattr(source,source_resource_spend) - ability.resource_cost)
    # If ability is a status granting ability set status on appropriate ability target
    if ability.type == 'abilitygrantstatus':
        if 'hostile' in ability.target:
            target.apply_status(ability.associated_status,ability.associated_status_duration)
            if log_mode == 2:
                print(source.name,'used',ability.name,'on',target.name)
                print(source.name,'has',getattr(source,source_resource_spend),'of',getattr(source,source_resource_max),'remaining')
        elif 'self' in ability.target:
            source.apply_status(ability.associated_status,ability.associated_status_duration)
            if log_mode == 2:
                print(source.name,'used',ability.name,'on',source.name)
                print(source.name,'has',getattr(source,source_resource_spend),'of',getattr(source,source_resource_max),'remaining')
    # If ability is direct damage and can target hostile then deal direct damage to the target
    if ability.type == 'abilitydamagedirect' and 'hostile' in ability.target:
        target.damage_creature_direct(ability.damage)
        if log_mode == 2:
            print(source.name,'used',ability.name,'on',target.name)
            print(source.name,'has',getattr(source,source_resource_spend),'of',getattr(source,source_resource_max),'remaining')
    # If ability is heal creature and can target self then heal source
    if ability.type == 'abilityhealcreature' and 'self' in ability.target:
        source.heal_creature(ability.healing)
        if log_mode == 2:
            print(source.name,'used',ability.name,'on',source.name)
            print(source.name,'has',getattr(source,source_resource_spend),'of',getattr(source,source_resource_max),'remaining')
    # If ability is affect creature
        #PLACEHOLDER

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
    elif (ability.speed == 'interruptible' and source_was_hit == 0) or ability.speed == 'uninterruptible':
        use_ability(source,target,ability,log_mode)

def run_solo_encounter(fighter_a,fighter_b,log_mode):
    'Run a solo encounter between fighter_a and fighter_b and return 0 for a draw, 1 for a fighter_a win and 2 for a fighter_b win'
    #Initialize round counter
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
        fighter_a_use_ability,fighter_b_use_ability = fighter_a.check_use_ability(),fighter_b.check_use_ability()

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
        hit_location_name_a = hit_location_names[hit_location_num_a]
        hit_location_name_b = hit_location_names[hit_location_num_b]
        
        # Perform the hit logic
        if 0 <= round_rand_hit < fighter_a_hit_chance :
            fighter_b.damage_creature(hit_location_num_b,fighter_a.damage)
            fighter_b_was_hit = 1
            if log_mode == 2:
                print(fighter_a.name, 'hits the', hit_location_name_b, 'of', fighter_b.name)
                print(fighter_b.name, hit_location_name_b, 'has', fighter_b.currhits[hit_location_num_b], 'of', fighter_b.maxhits[hit_location_num_b],'hits remaining')
        elif fighter_a_hit_chance <= round_rand_hit < (fighter_a_hit_chance+chance_trade) :
            fighter_b.damage_creature(hit_location_num_b,fighter_a.damage)
            fighter_a.damage_creature(hit_location_num_a,fighter_b.damage)
            fighter_a_was_hit,fighter_b_was_hit = 1,1
            if log_mode == 2:
                print(fighter_a.name, 'hits the', hit_location_name_b, 'of', fighter_b.name)
                print(fighter_b.name, hit_location_name_b, 'has', fighter_b.currhits[hit_location_num_b], 'of', fighter_b.maxhits[hit_location_num_b],'hits remaining')
                print(fighter_b.name, 'hits the', hit_location_name_a, 'of', fighter_a.name)
                print(fighter_a.name, hit_location_name_a, 'has', fighter_a.currhits[hit_location_num_a], 'of', fighter_a.maxhits[hit_location_num_a],'hits remaining')
        elif (fighter_a_hit_chance+chance_trade) <= round_rand_hit <= 1 :
            fighter_a.damage_creature(hit_location_num_a,fighter_b.damage)
            fighter_a_was_hit = 1
            if log_mode == 2:
                print(fighter_b.name, 'hits the', hit_location_name_a, 'of', fighter_a.name)
                print(fighter_a.name, hit_location_name_a, 'has', fighter_a.currhits[hit_location_num_a], 'of', fighter_a.maxhits[hit_location_num_a],'hits remaining')
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
