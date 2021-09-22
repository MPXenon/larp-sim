import classdefs
from copy import copy
from fightlogic import run_solo_encounter
from sys import exit
import jsonpickle

# Initialise other variables
# Currently assuming 10 rounds per minute as an approximation for spells with durations
rounds_per_minute = 10

# Order of initialisation becomes important for charged ablities
# Initialise any statuses infliced by charge delivering abilities
status_weakness = classdefs.Status('Weakened', status_damage_mod=-1)

# Initialise any abilities used to deliver charges
ability_weakness_discharge = classdefs.AbilityGrantStatus('Weakness','hostile','discharge',None,None,status_weakness,5*rounds_per_minute)

# Initialise combat statuses required for abilities
status_distracted = classdefs.Status('Distracted', status_rating_multi=0)
status_enhanced = classdefs.Status('Enhanced', status_damage_mod=1)
status_charge_weakness = classdefs.StatusCharged('Charge (Weakness)', ability_weakness_discharge)

# Initialise weapons
weapon_shield = classdefs.Weapon('Shield',1.5,[1,0.5,0.5,1,1,1])
weapon_off_hand = classdefs.Weapon('Off Hand Weapon',1.25,[1,3,1,0.5,2,0.5])
weapon_off_hand_short = classdefs.Weapon('Off Hand Short Weapon',1.3,[1,3,1,0.5,2,0.5])
weapon_two_handed = classdefs.Weapon('Two Handed',1.2,[1,3,1,0.5,1,1])
weapon_polearm = classdefs.Weapon('Polearm',2,[1,1,1,1,1,1.5])
weapon_select = weapon_shield,weapon_off_hand,weapon_off_hand_short,weapon_two_handed,weapon_polearm

# Initialise abilities
# Note : "Fast" abilities usually have minimum duration of 0 if they affect the current round only, while others should start at 1
ability_glimmer = classdefs.AbilityGrantStatus('Glimmer','hostile','fast','mana',1,status_distracted,0)
ability_enhancement = classdefs.AbilityGrantStatus('Enhancement',['self','friendly'],'fast','mana',1,status_enhanced,0)
ability_fireball = classdefs.AbilityDamageDirect('Fireball','hostile','interruptible','mana',4,3)
ability_smite_ranged = classdefs.AbilityDamageDirect('Smite','hostile','uninterruptible','spirit',1,6)
ability_heal_two = classdefs.AbilityHealCreature('Heal 2',['self','friendly'],'uninterruptible','spirit',1,2)
ability_spirit_armour = classdefs.AbilityAffectCreature('Spirit Armour',['self','friendly'],'uninterruptible','spirit',1,'glob_spirit_arm',3,'set')
ability_barrier_self = classdefs.AbilityAffectCreature('Barrier Self',['self','friendly'],'interruptible','mana',2,'glob_magic_arm',2,'set')
ability_weakness_charge = classdefs.AbilityGrantStatus('Weakness (Charge)','self','uninterruptible','spirit',1,status_charge_weakness,3)
ability_select = ability_glimmer,ability_enhancement,ability_fireball,ability_smite_ranged,ability_heal_two,ability_barrier_self,ability_weakness_charge

# Initialise some simple creatures and place into a tuple to select from
Peasant = classdefs.Locational('Peasant',1,[3,3,3,3,3,3],1)
Goblin = classdefs.Locational('Goblin',1,[2,2,2,2,3,3],1)
Skeleton = classdefs.Global('Skeleton',1,[6],1)
Zombie = classdefs.Global('Zombie',0.5,[9],2)
Lesser_Alkar = classdefs.Global('Lesser Alkar',1,[10],1,[weapon_off_hand])

Creature_Select = Peasant,Goblin,Skeleton,Zombie,Lesser_Alkar
character_list = []

# Get text input from the user to select combatants and number of fights to simulate
print('Choose creatures to fight:')
for x in range(len(Creature_Select)):
    print(str(x+1) + ' - ' + Creature_Select[x].name + ',')
print(str(len(Creature_Select)+1) + ' - Player Character')

# Get a custom character from file
def load_custom_character():
    selected_character = None
    # Load characters from file
    try:
        print("\nLoading...")  
        with open('characters.txt','r') as infile:
            character_list = jsonpickle.decode(infile.read())
    except:
        print("\nNo character file found.")
        print('Invalid selection, shutting down')
        exit()
    # Allow character selection
    while selected_character == None:
        print("\nAvailable characters:\n")
        for key in character_list:
            print(key)
            #print(character_list.get(key), "\n")
        selectchar_raw = input("\nSelect a character by name: ")
        selectchar_name = selectchar_raw.capitalize()
        if selectchar_name not in character_list:
            print("\nCharacter does not exist.")
        else:
            selected_character = character_list.get(selectchar_name)
    return selected_character


try:
    fighter_a_selection = int(input('Pick a number from 1-'+str(len(Creature_Select)+1)+' to select first creature : '))-1
    if fighter_a_selection in range(len(Creature_Select)):
        fighter_a = copy(Creature_Select[fighter_a_selection])
    elif fighter_a_selection == len(Creature_Select):
        fighter_a = copy(load_custom_character())
    else:
        raise
    fighter_b_selection = int(input('Pick a number from 1-'+str(len(Creature_Select)+1)+' to select second creature : '))-1
    if fighter_b_selection in range(len(Creature_Select)):
        fighter_b = copy(Creature_Select[fighter_b_selection])
    elif fighter_b_selection == len(Creature_Select):
        fighter_b = copy(load_custom_character())
    else:
        raise
    fight_count = int(input('Choose the number of fights to simulate: '))
    log_mode = int(input('Set logging mode: 0 - No Logging, 1 - Fight Outcomes Only, 2 - Round by Round: '))
    if log_mode not in [0,1,2]:
        raise
    
except:
    print('Invalid selection, shutting down')
    exit()

# Initialise Output Statistics
fighter_a_wincount,fighter_b_wincount,draw_count,fighter_a_hits_taken,fighter_b_hits_taken = 0,0,0,[],[]
fighter_a_mana_spent,fighter_a_spirit_spent,fighter_b_mana_spent,fighter_b_spirit_spent = [],[],[],[]

# Set up a loop to run the simulation a number of times and record the outcomes
for x in range(fight_count):
    # Display fight number if logging enabled
    if log_mode >=1:
        print('Fight',x+1,':')
    
    # Reset creatures to starting state
    fighter_a.initialize_creature()
    fighter_b.initialize_creature()

    #Run the fight
    y = run_solo_encounter(fighter_a,fighter_b,log_mode)

    # Calculate hits taken
    fighter_a_hits_taken.append(sum(fighter_a.maxhits)-sum(fighter_a.currhits))
    fighter_b_hits_taken.append(sum(fighter_b.maxhits)-sum(fighter_b.currhits))

    # Display fight outcomes if logging enabled
    if log_mode >= 1:
        print(fighter_a.name, 'took', fighter_a_hits_taken[-1], 'points of damage')
        print(fighter_b.name, 'took', fighter_a_hits_taken[-1], 'points of damage')
    
    # Calculate resources spent if creature is a TTPC
    if type(fighter_a).__name__ == 'TreasureTrapPC':
        fighter_a_mana_spent.append(fighter_a.get_resource_spent('mana'))
        fighter_a_spirit_spent.append(fighter_a.get_resource_spent('spirit'))
        if log_mode >= 1:
            if fighter_a_mana_spent[-1] > 0:
                print(fighter_a.name, 'used', fighter_a_mana_spent[-1],'points of mana')
            if fighter_a_spirit_spent[-1] > 0:
                print(fighter_a.name, 'used', fighter_a_spirit_spent[-1],'points of spirit')
    if type(fighter_b).__name__ == 'TreasureTrapPC':
        fighter_b_mana_spent.append(fighter_b.get_resource_spent('mana'))
        fighter_b_spirit_spent.append(fighter_b.get_resource_spent('spirit'))
        if log_mode >= 1:
            if fighter_b_mana_spent[-1] > 0:
                print(fighter_b.name, 'used', fighter_b_mana_spent[-1],'points of mana')
            if fighter_b_spirit_spent[-1] > 0:
                print(fighter_b.name, 'used', fighter_b_spirit_spent[-1],'points of spirit')

    # Record outcome           
    if y == 0:
        draw_count += 1
        if log_mode >= 1:
            print('Fight was a draw')
    elif y == 1:
        fighter_a_wincount += 1
        if log_mode >= 1:
            print(fighter_a.name,'won the fight')
    elif y == 2:
        fighter_b_wincount += 1
        if log_mode >= 1:
            print(fighter_b.name,'won the fight')

# Generalised Output stats
print(fighter_a.name, 'won', fighter_a_wincount, '(', round((fighter_a_wincount/fight_count)*100,2), '% ) fights')
print(fighter_b.name, 'won', fighter_b_wincount, '(', round((fighter_b_wincount/fight_count)*100,2), '% ) fights')
print(draw_count, '(', round((draw_count/fight_count)*100,2), '% ) fights ended in a draw')
print(fighter_a.name, 'took', round(sum(fighter_a_hits_taken)/len(fighter_a_hits_taken),2),'points of damage on average')
print(fighter_b.name, 'took', round(sum(fighter_b_hits_taken)/len(fighter_b_hits_taken),2),'points of damage on average')
if sum(fighter_a_mana_spent) > 0:
    print(fighter_a.name, 'used', round(sum(fighter_a_mana_spent)/len(fighter_a_mana_spent),2),'mana on average')
if sum(fighter_a_spirit_spent) > 0:
    print(fighter_a.name, 'used', round(sum(fighter_a_spirit_spent)/len(fighter_a_spirit_spent),2),'spirit on average')
if sum(fighter_b_mana_spent) > 0:
    print(fighter_b.name, 'used', round(sum(fighter_b_mana_spent)/len(fighter_b_mana_spent),2),'mana on average')
if sum(fighter_b_spirit_spent) > 0:
    print(fighter_b.name, 'used', round(sum(fighter_b_spirit_spent)/len(fighter_b_spirit_spent),2),'spirit on average')

input('Press Enter to Exit.....')
