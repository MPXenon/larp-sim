import creature
import weapon
import abilities
import status
from copy import copy
from fightlogic import run_solo_encounter
from sys import exit

# Initialise combat statuses required for abilities
status_distracted = status.Status('Distracted', status_rating_multi=0)
status_enhanced = status.Status('Enhanced', status_damage_mod=1)

# Initialise weapons
weapon_shield = weapon.Weapon('Shield',1.5,[1,0.5,0.5,1,1,1])
weapon_off_hand = weapon.Weapon('Off Hand Weapon',1.25,[1,3,1,0.5,2,0.5])
weapon_off_hand_short = weapon.Weapon('Off Hand Short Weapon',1.3,[1,3,1,0.5,2,0.5])
weapon_two_handed = weapon.Weapon('Two Handed',1.2,[1,3,1,0.5,1,1])
weapon_polearm = weapon.Weapon('Two Handed',2,[1,1,1,1,1,1.5])
weapon_select = weapon_shield,weapon_off_hand,weapon_off_hand_short,weapon_two_handed,weapon_polearm

# Initialise abilities
# Note : "Fast" abilities usually have minimum duration of 0 if they affect the current round only, while others should start at 1
ability_glimmer = abilities.AbilityGrantStatus('Glimmer','hostile','fast','mana',1,status_distracted,0)
ability_enhancement = abilities.AbilityGrantStatus('Enhancement',['self','friendly'],'fast','mana',1,status_enhanced,0)
ability_fireball = abilities.AbilityDamageDirect('Fireball','hostile','interruptible','mana',4,3)
ability_smite_ranged = abilities.AbilityDamageDirect('Smite','hostile','uninterruptible','spirit',1,6)
ability_heal_two = abilities.AbilityHealCreature('Heal 2',['self','friendly'],'uninterruptible','spirit',1,2)
ability_select = ability_glimmer,ability_enhancement,ability_fireball,ability_smite_ranged,ability_heal_two

# Initialise some simple creatures and place into a tuple to select from
Fighter = creature.TreasureTrapPC('Fighter',1,[4,4,4,4,4,4],1,[weapon_shield],[],[1,1,1,1,1,1])
Scout = creature.TreasureTrapPC('Scout',1,[3,3,3,3,3,3],1,[weapon_off_hand_short],[],[1,1,1,1,1,1],1)
Berserker = creature.Locational('Berserker',1,[3,3,3,3,3,3],2,[weapon_two_handed])
Peasant = creature.Locational('Peasant',1,[3,3,3,3,3,3],1)
Goblin = creature.Locational('Goblin',1,[2,2,2,2,3,3],1)
Skeleton = creature.Global('Skeleton',1,[6],1)
Zombie = creature.Global('Zombie',0.5,[9],2)
Lesser_Alkar = creature.Global('Lesser Alkar',1,[10],1,[weapon_off_hand])
Darkness_Warlock = creature.TreasureTrapPC('Dark Warlock',1,[3,3,3,3,3,3],1,[],[ability_glimmer],[0,0,0,0,0,0],0,0,0,10)
Fire_Warlock = creature.TreasureTrapPC('Fire Warlock',1,[3,3,3,3,3,3],1,[],[ability_enhancement],[0,0,0,0,0,0],0,0,0,10)
Fireball_Pyromancer = creature.TreasureTrapPC('Fireball Pyromancer',1,[3,3,3,3,3,3],1,[],[ability_fireball],[0,0,0,0,0,0],0,0,0,24)
Blaster_Priest = creature.TreasureTrapPC('Blaster Priest',1,[3,3,3,3,3,3],1,[],[ability_smite_ranged],[0,0,0,0,0,0],0,2,0,0,5)
Basic_Healbot_Priest = creature.TreasureTrapPC('Basic Healbot Priest',1,[3,3,3,3,3,3],1,[],[ability_heal_two],[0,0,0,0,0,0],0,0,0,0,5)
Creature_Select = Fighter,Scout,Berserker,Peasant,Goblin,Skeleton,Zombie,Lesser_Alkar,Darkness_Warlock,Fire_Warlock,Fireball_Pyromancer,Blaster_Priest,Basic_Healbot_Priest

# Very primitive Function to allow users to input a simple TT character from stdin
def create_custom_character():
    try:
        char_name = str(input('Input character name:'))
        char_rating = 1
        char_hits_crit = int(input('Input hits per critical (head/body) location as an integer:'))
        char_hits_limb = int(input('Input hits per limb location as an integer:'))
        char_hits_max = [char_hits_limb for i in range(6)]
        char_hits_max[0] = char_hits_crit
        char_hits_max[2] = char_hits_crit
        char_damage = int(input('Input damage call as an integer :'))
        char_weapon_select = int(input('Select weapon: 0 - 42", 1 - 42" and Shield, 2 - Ambidex 42", 3 - Ambidex 42" and 24", 4 - 60" Two Hander, 5 - 72" Polearm :'))
        if char_weapon_select == 0:
            char_weapon = []
        elif 0 < char_weapon_select <= 5:
            char_weapon = [weapon_select[char_weapon_select-1]]
        else:
            raise
        char_ability_select = int(input('Select one ability: 0 - None, 1 - Glimmer, 2 - Enhancement, 3 - Fireball, 4 - Ranged Smite , 5 - Heal 2 :'))
        if char_ability_select == 0:
            char_ability = []
        elif 0 < char_ability_select <= 5:
            char_ability = [ability_select[char_ability_select-1]]
        else:
            raise
        char_armour_value = int(input('Input armour hits per location as an integer (for now all locations will be armoured the same):'))
        char_loc_armour = [char_armour_value for i in range(6)]
        char_dac = int(input('Input points of DAC as an integer:'))
        char_spirit_arm = int(input('Input points of Spirit Armour as an integer:'))
        char_magic_arm = int(input('Input points of Magic Armour as an integer:'))
        char_mana = int(input('Input points of Mana as an integer:'))
        char_spirit = int(input('Input points of Spirit as an integer:'))

    except:
        print('Invalid selection, shutting down')
        exit()

    return creature.TreasureTrapPC(char_name,char_rating,char_hits_max,char_damage,char_weapon,char_ability,char_loc_armour,char_dac,char_spirit_arm,char_magic_arm,char_mana,char_spirit)

# Get text input from the user to select combatants and number of fights to simulate
print('Choose creatures to fight:')
print('1 - Fighter, 2 - Scout, 3 - Berserker, 4 - Peasant, 5- Goblin, 6 - Skeleton, 7 - Zombie, 8 - Lesser Alkar, 9 - Darkness Warlock, 10 - Fire Warlock, 11 - Fireball Pyromancer, 12 - Blaster Priest, 13 - Basic Healbot Priest, 14 - Custom')

try:
    fighter_a_selection = int(input('Pick a number from 1-13 to select first creature :'))-1
    fighter_b_selection = int(input('Pick a number from 1-13 to select second creature :'))-1
    fight_count = int(input('Choose the number of fights to simulate:'))
    if fighter_a_selection in range(len(Creature_Select)):
        fighter_a = copy(Creature_Select[fighter_a_selection])
    elif fighter_a_selection == len(Creature_Select):
        fighter_a = create_custom_character()
    else:
        raise
    if fighter_b_selection in range(len(Creature_Select)):
        fighter_b = copy(Creature_Select[fighter_b_selection])
    elif fighter_b_selection == len(Creature_Select):
        fighter_b = create_custom_character()
    else:
        raise
    log_mode = int(input('Set logging mode: 0 - No Logging, 1 - Fight Outcomes Only, 2 - Round by Round'))
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
