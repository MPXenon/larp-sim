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
ability_harm_discharge = classdefs.AbilityDamageLocation('Harm','hostile','discharge',None,None,2)
ability_shock_discharge = classdefs.AbilityDamageLocation('Shock','hostile','discharge',None,None,2)

# Initialise combat statuses required for abilities
status_distracted = classdefs.Status('Distracted', status_rating_multi=0)
status_enhanced = classdefs.Status('Enhanced', status_damage_mod=1)
status_charge_weakness = classdefs.StatusCharged('Charge (Weakness)', ability_weakness_discharge,status_damage_multi=0)
status_charge_harm = classdefs.StatusCharged('Charge (Harm)', ability_harm_discharge,status_damage_multi=0)
status_charge_shock = classdefs.StatusCharged('Charge (Shock)', ability_shock_discharge,status_damage_multi=0)

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
ability_harm_charge = classdefs.AbilityGrantStatus('Harm (Charge)','self','uninterruptible','spirit',1,status_charge_harm,3)
ability_shock_charge = classdefs.AbilityGrantStatus('Shock (Charge)','self','uninterruptible','mana',2,status_charge_shock,3)
ability_select = ability_glimmer,ability_enhancement,ability_fireball,ability_smite_ranged,ability_heal_two,ability_barrier_self,ability_weakness_charge

# Initialise some simple creatures and place into a list to select from
Fighter = classdefs.TreasureTrapPC('Fighter',1,[4,4,4,4,4,4],1,[weapon_shield],[],[1,1,1,1,1,1])
Scout = classdefs.TreasureTrapPC('Scout',1,[3,3,3,3,3,3],1,[weapon_off_hand_short],[],[1,1,1,1,1,1],1)
Berserker = classdefs.TreasureTrapPC('Berserker',1,[3,3,3,3,3,3],2,[weapon_two_handed],[],[1,1,1,1,1,1],1)
Darkness_Warlock = classdefs.TreasureTrapPC('Dark warlock',1,[3,3,3,3,3,3],1,[],[ability_glimmer],[0,0,0,0,0,0],0,0,0,10)
Fire_Warlock = classdefs.TreasureTrapPC('Fire warlock',1,[3,3,3,3,3,3],1,[],[ability_enhancement],[0,0,0,0,0,0],0,0,0,10)
Fireball_Pyromancer = classdefs.TreasureTrapPC('Fireball pyromancer',1,[3,3,3,3,3,3],1,[],[ability_fireball],[0,0,0,0,0,0],0,0,0,24)
Blaster_Priest = classdefs.TreasureTrapPC('Blaster priest',1,[3,3,3,3,3,3],1,[],[ability_smite_ranged],[0,0,0,0,0,0],0,2,0,0,5)
Basic_Healbot_Priest = classdefs.TreasureTrapPC('Basic healbot priest',1,[3,3,3,3,3,3],1,[],[ability_heal_two],[0,0,0,0,0,0],0,0,0,0,5)
Basic_Armour_Priest = classdefs.TreasureTrapPC('Basic armour priest',1,[3,3,3,3,3,3],1,[],[ability_spirit_armour],[0,0,0,0,0,0],0,0,0,0,5)
Basic_Weakness_Priest = classdefs.TreasureTrapPC('Basic weakness priest',1,[3,3,3,3,3,3],1,[],[ability_weakness_charge],[0,0,0,0,0,0],0,0,0,0,5)
Basic_Harm_Priest = classdefs.TreasureTrapPC('Basic harm priest',1,[3,3,3,3,3,3],1,[],[ability_harm_charge],[0,0,0,0,0,0],0,0,0,0,5)
Basic_Shock_Warlock = Fire_Warlock = classdefs.TreasureTrapPC('Basic shock warlock',1,[3,3,3,3,3,3],1,[],[ability_shock_charge],[0,0,0,0,0,0],0,0,0,10)
character_names = ['Fighter','Scout','Berserker','Dark warlock','Fire warlock','Fireball pyromancer','Blaster priest','Basic healbot priest','Basic armour priest','Basic weakness priest','Basic harm priest','Basic shock warlock']
character_objects = [Fighter,Scout,Berserker,Darkness_Warlock,Fire_Warlock,Fireball_Pyromancer,Blaster_Priest,Basic_Healbot_Priest,Basic_Armour_Priest,Basic_Weakness_Priest,Basic_Harm_Priest,Basic_Shock_Warlock]

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