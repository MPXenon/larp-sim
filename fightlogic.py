# Module containing various versions of the fight logic
import random
from sys import exit

# Base chance to trade blows instead of either party getting a clean hit when their skill is equal
chance_trade_base = 0.5 

def run_solo_encounter(fighter_a,fighter_b):
    'Run a solo encounter between fighter_a and fighter_b and return 0 for a draw, 1 for a fighter_a win and 2 for a fighter_b win'
    #Initialize round counter
    round_count = 0
    
    # Round Loops
    while 1:
        # Increment and Print Round tracker 
        round_count += 1

        # Update Statuses
        fighter_a.update_status()
        fighter_b.update_status()

        # Store the fighter ratings as temp variables to avoid repetition of the getter logic
        _fighter_a_rating = fighter_a.rating
        _fighter_b_rating = fighter_b.rating
        
        # Exception for both fighters having a rating of Zero - skip the round
        if _fighter_a_rating == 0 and _fighter_b_rating == 0:
            continue

        # Calculate the variables for working out round winner  - scaled by the skill gap of the creatures
        chance_trade = min(_fighter_a_rating,_fighter_b_rating)/max(_fighter_a_rating,_fighter_b_rating)*chance_trade_base
        fighter_a_hit_chance = _fighter_a_rating*((1-chance_trade)/(_fighter_a_rating+_fighter_b_rating))

        # Get all the random numbers required
        round_rand_hit = random.random()
        hit_location_a_num = fighter_a.determine_hit_location()
        hit_location_b_num = fighter_b.determine_hit_location()

        # Check if the parties will use any abilities - currently does nothing but report that a spell should be cast
        fighter_a_use_ability, fighter_a_use_resource = fighter_a.check_use_ability()
        fighter_b_use_ability, fighter_b_use_resource = fighter_b.check_use_ability()
        # At this point we know weather each fighter will use an ability and of which type, but not which one
        # PLACEHOLDER

        # Perform the hit logic
        if 0 <= round_rand_hit < fighter_a_hit_chance :
            fighter_b.damage_creature(hit_location_b_num,fighter_a.damage)
        elif fighter_a_hit_chance <= round_rand_hit < (fighter_a_hit_chance+chance_trade) :
            fighter_b.damage_creature(hit_location_b_num,fighter_a.damage)
            fighter_a.damage_creature(hit_location_a_num,fighter_b.damage)
        elif (fighter_a_hit_chance+chance_trade) <= round_rand_hit <= 1 :
            fighter_a.damage_creature(hit_location_a_num,fighter_b.damage)
        else :
            print('Error: Unspecified combat round outcome')
            exit()

        # Perform end of round status checks
        x = fighter_a.check_incapacitated()
        y = fighter_b.check_incapacitated()
        
        # Output Fight Result
        if x == 1 and y == 1:
            return 0
        elif y == 1:
            return 1
        elif x == 1:

            return 2
