import classdefs
from copy import copy
from fightlogic import run_solo_encounter
from sys import exit
import jsonpickle

# Initialise combat statuses required for abilities
status_distracted = classdefs.Status('Distracted', status_rating_multi=0)
status_enhanced = classdefs.Status('Enhanced', status_damage_mod=1)

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
ability_select = ability_glimmer,ability_enhancement,ability_fireball,ability_smite_ranged,ability_heal_two,ability_barrier_self

# Initialise some simple creatures and place into a tuple to select from
Fighter = classdefs.TreasureTrapPC('Fighter',1,[4,4,4,4,4,4],1,[weapon_shield],[],[1,1,1,1,1,1])
Scout = classdefs.TreasureTrapPC('Scout',1,[3,3,3,3,3,3],1,[weapon_off_hand_short],[],[1,1,1,1,1,1],1)
Berserker = classdefs.TreasureTrapPC('Berserker',1,[3,3,3,3,3,3],2,[weapon_two_handed],[],[1,1,1,1,1,1],1)
Darkness_Warlock = classdefs.TreasureTrapPC('Dark warlock',1,[3,3,3,3,3,3],1,[],[ability_glimmer],[0,0,0,0,0,0],0,0,0,10)
Fire_Warlock = classdefs.TreasureTrapPC('Fire warlock',1,[3,3,3,3,3,3],1,[],[ability_enhancement],[0,0,0,0,0,0],0,0,0,10)
Fireball_Pyromancer = classdefs.TreasureTrapPC('Fireball pyromancer',1,[3,3,3,3,3,3],1,[],[ability_fireball],[0,0,0,0,0,0],0,0,0,24)
Blaster_Priest = classdefs.TreasureTrapPC('Blaster priest',1,[3,3,3,3,3,3],1,[],[ability_smite_ranged],[0,0,0,0,0,0],0,2,0,0,5)
Basic_Healbot_Priest = classdefs.TreasureTrapPC('Basic healbot priest',1,[3,3,3,3,3,3],1,[],[ability_heal_two],[0,0,0,0,0,0],0,0,0,0,5)
Basic_Armour_Priest = classdefs.TreasureTrapPC('Basic armour priest',1,[3,3,3,3,3,3],1,[],[ability_spirit_armour],[0,0,0,0,0,0],0,0,0,0,5)
character_names = ['Fighter','Scout','Berserker','Dark warlock','Fire warlock','Fireball pyromancer','Blaster priest','Basic healbot priest','Basic armour priest']
character_objects = [Fighter,Scout,Berserker,Darkness_Warlock,Fire_Warlock,Fireball_Pyromancer,Blaster_Priest,Basic_Healbot_Priest,Basic_Armour_Priest]

character_dict = {}
for key in character_names:
    for value in character_objects:
        character_dict[key] = value
        character_objects.remove(value)
        break  

# Save characters to file
print("\nSaving...")
with open('characters.txt','w') as outfile:
    outfile.write(jsonpickle.encode(character_dict))
print("\nSaving complete.")