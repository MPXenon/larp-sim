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

        # Reset hit check variables
        fighter_a_was_hit,fighter_b_was_hit = 0,0

        # Check if the parties will use any abilities and return the ones they will use
        fighter_a_use_ability = fighter_a.check_use_ability()
        fighter_b_use_ability = fighter_b.check_use_ability()

        # Implement logic for using fast abilities - need to do this before we calculate fighter ratings as it can modify them
        # Note : "Combo's" like Glimmer + Enhancement would need to implemented as their own "Ability" - since only one ability is ever used per round
        if fighter_a_use_ability != None:
            if fighter_a_use_ability.speed == 'fast':
                # Spend resource of fighter a
                # Note : Should probably implement resource spend as a class method to be cleaner
                fighter_a_resource_spend = fighter_a_use_ability.resource_activate + '_points'
                setattr(fighter_a,fighter_a_resource_spend,getattr(fighter_a,fighter_a_resource_spend) - fighter_a_use_ability.resource_cost)
                # Set status on ability target
                # Note : This code is re-used like 4 times, can it be a method?
                if 'hostile' in fighter_a_use_ability.target:
                    fighter_b.apply_status(fighter_a_use_ability.associated_status,fighter_a_use_ability.associated_status_duration)
                elif 'self' in fighter_a_use_ability.target:
                    fighter_a.apply_status(fighter_a_use_ability.associated_status,fighter_a_use_ability.associated_status_duration)

        if fighter_b_use_ability != None:
            if fighter_b_use_ability.speed == 'fast':
                # Spend resource of fighter b
                fighter_b_resource_spend = fighter_b_use_ability.resource_activate + '_points'
                setattr(fighter_b,fighter_b_resource_spend,getattr(fighter_b,fighter_b_resource_spend) - fighter_b_use_ability.resource_cost)
                # Set status on ability target
                if 'hostile' in fighter_b_use_ability.target:
                    fighter_a.apply_status(fighter_b_use_ability.associated_status,fighter_b_use_ability.associated_status_duration)
                elif 'self' in fighter_b_use_ability.target:
                    fighter_b.apply_status(fighter_b_use_ability.associated_status,fighter_b_use_ability.associated_status_duration)

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
        
        # Perform the hit logic
        if 0 <= round_rand_hit < fighter_a_hit_chance :
            fighter_b.damage_creature(fighter_b.determine_hit_location(),fighter_a.damage)
            fighter_b_was_hit = 1
        elif fighter_a_hit_chance <= round_rand_hit < (fighter_a_hit_chance+chance_trade) :
            fighter_b.damage_creature(fighter_b.determine_hit_location(),fighter_a.damage)
            fighter_a.damage_creature(fighter_a.determine_hit_location(),fighter_b.damage)
            fighter_a_was_hit,fighter_b_was_hit = 1,1
        elif (fighter_a_hit_chance+chance_trade) <= round_rand_hit <= 1 :
            fighter_a.damage_creature(fighter_a.determine_hit_location(),fighter_b.damage)
            fighter_a_was_hit = 1
        else :
            print('Error: Unspecified combat round outcome')
            exit()

        # Perform end of round status checks
        x = fighter_a.check_incapacitated()
        y = fighter_b.check_incapacitated()

        # Implement logic for using interruptible (if not hit while casting) and uniterruptible abilities
        if fighter_a_use_ability != None:
            if (fighter_a_use_ability.speed == 'interruptible' and fighter_a_was_hit == 0) or fighter_a_use_ability.speed == 'uninterruptible':
                # Set status on ability target
                if 'hostile' in fighter_a_use_ability.target:
                    fighter_b.apply_status(fighter_a_use_ability.associated_status,fighter_a_use_ability.associated_status_duration)
                elif 'self' in fighter_a_use_ability.target:
                    fighter_a.apply_status(fighter_a_use_ability.associated_status,fighter_a_use_ability.associated_status_duration)
        
        if fighter_b_use_ability != None:
            if (fighter_b_use_ability.speed == 'interruptible' and fighter_b_was_hit == 0) or fighter_a_use_ability.speed == 'uninterruptible':
                 # Set status on ability target
                if 'hostile' in fighter_b_use_ability.target:
                    fighter_a.apply_status(fighter_b_use_ability.associated_status,fighter_b_use_ability.associated_status_duration)
                elif 'self' in fighter_b_use_ability.target:
                    fighter_b.apply_status(fighter_b_use_ability.associated_status,fighter_b_use_ability.associated_status_duration)

        # Output Fight Result
        if x == 1 and y == 1:
            return 0
        elif y == 1:
            return 1
        elif x == 1:

            return 2
