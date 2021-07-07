import creature
import weapon
import abilities
import status
from copy import copy
from fightlogic import run_solo_encounter
from sys import exit

# Initialise combat statuses required for abilities
# Note : These are "safe" to use with global creatures
status_distracted = status.Status('Distracted', status_rating_multi=0)
status_enhanced = status.Status('Enhanced', status_damage_mod=1)

# Initialise weapons
weapon_shield = weapon.Weapon('Shield',1.5,[1,0.5,0.5,1,1,1])
weapon_off_hand = weapon.Weapon('Off Hand Weapon',1.25,[1,3,1,0.5,2,0.5])
weapon_off_hand_short = weapon.Weapon('Off Hand Short Weapon',1.3,[1,3,1,0.5,2,0.5])
weapon_two_handed = weapon.Weapon('Two Handed',1.2,[1,3,1,0.5,1,1])
weapon_polearm = weapon.Weapon('Two Handed',2,[1,1,1,1,1,1.5])

# Initialise abilities
# Note : "Fast" abilities usually have minimum duration of 0 if they affect the current round only, while others should start at 1
ability_glimmer = abilities.AbilityGrantStatus('Glimmer','hostile','fast','mana',1,status_distracted,0)
ability_enhancement = abilities.AbilityGrantStatus('Enhancement',['self','friendly'],'fast','mana',1,status_enhanced,0)
ability_fireball = abilities.AbilityDamageDirect('Fireball','hostile','interruptible','mana',4,3)
ability_smite_ranged = abilities.AbilityDamageDirect('Smite','hostile','uninterruptible','spirit',1,6)
ability_heal_two = abilities.AbilityHealCreature('Heal 2',['self','friendly'],'uninterruptible','spirit',1,2)

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

# Get text input from the user to select combatants and number of fights to simulate
print('Choose creatures to fight:')
print('1 - Fighter, 2 - Scout, 3 - Berserker, 4 - Peasant, 5- Goblin, 6 - Skeleton, 7 - Zombie, 8 - Lesser Alkar, 9 - Darkness Warlock, 10 - Fire Warlock, 11 - Fireball Pyromancer, 12 - Blaster Priest, 13 - Basic Healbot Priest')

try:
    fighter_a_selection = int(input('Pick a number from 1-13 to select first creature :'))-1
    fighter_b_selection = int(input('Pick a number from 1-13 to select second creature :'))-1
    fight_count = int(input('Choose the number of fights to simulate:'))
    fighter_a = copy(Creature_Select[fighter_a_selection])
    fighter_b = copy(Creature_Select[fighter_b_selection])
except:
    print('Invalid selection, shutting down')
    exit()

# Initialise Output Statistics
fighter_a_wincount,fighter_b_wincount,draw_count,fighter_a_hits_taken,fighter_b_hits_taken, = 0,0,0,[],[]

# Set up a loop to run the simulation a number of times and record the outcomes
for x in range(fight_count):

    # Reset creatures to starting state
    fighter_a.initialize_creature()
    fighter_b.initialize_creature()

    #Run the fight
    y = run_solo_encounter(fighter_a,fighter_b)
    
    if y == 0:
        draw_count += 1
    elif y == 1:
        fighter_a_wincount += 1
    elif y == 2:
        fighter_b_wincount += 1

    # Calculate hits taken
    fighter_a_hits_taken.append(sum(fighter_a.maxhits)-sum(fighter_a.currhits))
    fighter_b_hits_taken.append(sum(fighter_b.maxhits)-sum(fighter_b.currhits))

    # Calculate resources spent
    # PLACEHOLDER

# Generalised Output stats
print(fighter_a.name, 'won', fighter_a_wincount, '(', round((fighter_a_wincount/fight_count)*100,2), '% ) fights')
print(fighter_b.name, 'won', fighter_b_wincount, '(', round((fighter_b_wincount/fight_count)*100,2), '% ) fights')
print(draw_count, '(', round((draw_count/fight_count)*100,2), '% ) fights ended in a draw')
print(fighter_a.name, 'took', round(sum(fighter_a_hits_taken)/len(fighter_a_hits_taken),2),'points of damage on average')
print(fighter_b.name, 'took', round(sum(fighter_b_hits_taken)/len(fighter_b_hits_taken),2),'points of damage on average')