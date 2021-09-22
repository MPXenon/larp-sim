import classdefs
import jsonpickle

def main():
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
    weapon_sword = classdefs.Weapon('Sword',1,[1,1,1,1,1,1])
    weapon_shield = classdefs.Weapon('Shield',1.5,[1,0.5,0.5,1,1,1])
    weapon_off_hand = classdefs.Weapon('Off Hand Weapon',1.25,[1,3,1,0.5,2,0.5])
    weapon_off_hand_short = classdefs.Weapon('Off Hand Short Weapon',1.3,[1,3,1,0.5,2,0.5])
    weapon_two_handed = classdefs.Weapon('Two Handed',1.2,[1,3,1,0.5,1,1])
    weapon_polearm = classdefs.Weapon('Polearm',2,[1,1,1,1,1,1.5])
    weapon_select = weapon_sword,weapon_shield,weapon_off_hand,weapon_off_hand_short,weapon_two_handed,weapon_polearm

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
    ability_select = ability_glimmer,ability_enhancement,ability_fireball,ability_smite_ranged,ability_heal_two,ability_spirit_armour,ability_barrier_self,ability_weakness_charge,ability_harm_charge,ability_shock_charge
    
    # Initialise variables
    hit_location_names = ['Head','Off Hand','Body','Favoured Hand','Off Leg','Favoured Leg']
    choice = None
    character_list = {}

    # Initialise Menus
    main_menu_string = """
    Treasure Trap Character Creator
    =================

    Please choose your option below:
    0 - Quit
    1 - Create New Character
    2 - Edit Existing Character
    3 - Delete Character
    4 - List All Characters
    5 - Save All Characters
    6 - Load All Characters
    """

    location_menu_string = """
    Choose location to edit
    =================
    0 - Done
    1 - Head
    2 - Off Hand
    3 - Body
    4 - Favoured Hand
    5 - Off Leg
    6 - Favoured Leg
    """

    edit_menu_string = """
    Choose statistic to edit
    =================
    0 - Done
    1 - Hits
    2 - Locational Armour
    3 - Global Armour
    4 - Resources
    5 - Weapons
    6 - Abilities
    """
    # Main Code
    # Autoload characters from file
    try:
        print("\nLoading...")  
        with open('characters.txt','r') as infile:
            character_list = jsonpickle.decode(infile.read())
    except:
        print("\nNo character file found.")

    while choice != "0":

        print(main_menu_string) 
        choice = input("Choice: ")
        print()

        # Exit
        if choice == "0":
            print("\nExiting...")

        # Create new character
        elif choice == "1":
            raw_name = input("Input character name: ")
            char_name = raw_name.capitalize()
            if char_name in character_list:
                print("\nA character with this name already exists. Please select a different name.")
            else:
                # Get hits from input
                try:
                    char_hits_crit = int(input('\nInput hits per critical (head/body) location as an integer:'))
                    char_hits_limb = int(input('\nInput hits per limb location as an integer:'))
                except ValueError:
                    print("\nInvalid values, hits defaulted to 3/loc.")
                    char_hits_crit = 3
                    char_hits_limb = 3
                # Character skill rating - set to 1 - may later include some options
                char_rating = 1
                # Actually set the characters hits
                char_hits_max = [char_hits_limb for i in range(6)]
                char_hits_max[0] = char_hits_crit
                char_hits_max[2] = char_hits_crit
                # Get damage from input
                try:
                    char_damage = int(input('\nInput damage call as an integer :'))
                except ValueError:
                    print("\nInvalid value, damage defaulted to 1.")
                    char_damage = 1
                # Get locational armour from input
                char_loc_armour = [0,0,0,0,0,0]
                char_loc_select = None
                while char_loc_select != -1:
                    print(location_menu_string)
                    char_loc_select = int(input("Choice: "))-1
                    if char_loc_select in range(0,6):
                        print('\nArmour value for ' + str(hit_location_names[char_loc_select]) + ' is currently set to ' + str(char_loc_armour[char_loc_select]))
                        try:
                            char_loc_armour[char_loc_select] = int(input('\nInput armour hits for location as an integer:'))
                        except ValueError:
                            print('\nInvalid choice, Armour value for ' + str(hit_location_names[char_loc_select]) + ' will remain as ' + str(char_loc_armour[char_loc_select]))
                    elif char_loc_select == -1:
                        continue
                    else:
                        print('\nInvalid choice.')
                # Get global armour from input
                try:
                    char_spirit_arm = int(input('\nInput points of Spirit Armour as an integer:'))
                except ValueError:
                    print("\nInvalid value, Spirit Armour defaulted to 0.")
                    char_spirit_arm = 0
                try:
                    char_magic_arm = int(input('\nInput points of Magic Armour as an integer:'))
                except ValueError:
                    print("\nInvalid value, Magic Armour defaulted to 0.")
                    char_magic_arm = 0
                try:
                    char_dac = int(input('\nInput points of DAC as an integer:'))
                except ValueError:
                    print("\nInvalid value, DAC defaulted to 0.")
                    char_dac = 0
                # Get Resources from input
                try:
                    char_spirit = int(input('\nInput points of Spirit as an integer:'))
                except ValueError:
                    print("\nInvalid value, Spirit points defaulted to 0.")
                    char_spirit = 0
                try:
                    char_mana = int(input('\nInput points of Mana as an integer:'))
                except ValueError:
                    print("\nInvalid value, Mana points defaulted to 0.")
                    char_mana = 0
                # Select a weapon
                print('\nWIP - Choose a single character weapon:')
                print('\nChoose a weapon:')
                for x in range(len(weapon_select)):
                    print(str(x+1) + ' - ' + weapon_select[x].name + ',')
                try: 
                    char_weapon_select = int(input('\nChoice:'))
                    if char_weapon_select-1 not in range(len(weapon_select)):
                        raise
                except ValueError:
                    print("\nInvalid value, defaulted to single sword")
                    char_weapon_select = 1
                char_weapon = [weapon_select[char_weapon_select-1]]
                # Add ability/ies to character
                print('\nWIP - Choose a single character ability:')
                print('0 - No Abilities')
                for x in range(len(ability_select)):
                    print(str(x+1) + ' - ' + ability_select[x].name + ',')
                try: 
                    char_ability_select = int(input('\nChoice:'))
                    if char_ability_select == 0:
                        char_ability = []
                    elif char_ability_select-1 not in range(len(ability_select)):
                        raise ValueError
                    else:
                        char_ability = [ability_select[char_ability_select-1]]
                except ValueError:
                    print("\nInvalid value, defaulted to no abilities")
                    char_ability = []
                # Create character and add to the character list
                character_list.update({char_name: classdefs.TreasureTrapPC(char_name,char_rating,char_hits_max,char_damage,char_weapon,char_ability,char_loc_armour,char_dac,char_spirit_arm,char_magic_arm,char_mana,char_spirit)})          

        # Edit character
        elif choice == "2":
            print("\nAvailable characters:\n")
            for key in character_list:
                print(key)
                print(character_list.get(key), "\n")
            editchar_raw = input("Select a character to edit: ")
            editchar_name = editchar_raw.capitalize()
            if editchar_name not in character_list:
                print("\nCharacter does not exist.")
            else:
                editchar = character_list.get(editchar_name)
                edit_choice = None
                while edit_choice != "0":
                    print(edit_menu_string)
                    edit_choice = input("Choice: ")

                    # Edit Locational Hits
                    if edit_choice == "1":
                        loc_choice = None
                        while loc_choice != -1:
                            print("\nChoose location to edit hits :")
                            print("\n=================")
                            print("\n0 - Done")
                            for x in range(len(hit_location_names)):
                                print(str(x+1) + ' - ' + hit_location_names[x] + ' : '+ str(editchar.maxhits[x]))
                            loc_choice = int(input("\nChoice :"))-1
                            if loc_choice == -1:
                                continue
                            elif loc_choice in range(len(hit_location_names)):
                                try:
                                    editchar.maxhits[loc_choice] = int(input('\nInput hit points as an integer:'))
                                except ValueError:
                                    print("\nInvalid value, hits not changed")
                            else:
                                print("\nInvalid choice.")

                    #Edit Locational Armour
                    elif edit_choice == "2":
                        loc_choice = None
                        while loc_choice != -1:
                            print("\nChoose location to edit armour:")
                            print("\n=================")
                            print("\n0 - Done")
                            for x in range(len(hit_location_names)):
                                print(str(x+1) + ' - ' + hit_location_names[x] + ' : '+ str(editchar.loc_armour_max[x]))
                            loc_choice = int(input("\nChoice :"))-1
                            if loc_choice == -1:
                                continue
                            elif loc_choice in range(len(hit_location_names)):
                                try:
                                    editchar.loc_armour_max[loc_choice] = int(input('\nInput armour value as an integer:'))
                                except ValueError:
                                    print("\nInvalid value, armour not changed")
                            else:
                                print("\nInvalid choice.")

                    # Edit locational armour
                    elif edit_choice == "3":
                        print('Spirit armour : ' + str(editchar.glob_spirit_arm_max))
                        print('Magic armour : ' + str(editchar.glob_magic_arm_max))
                        print('DAC: ' + str(editchar.glob_dac_max))
                        try:
                            editchar.glob_spirit_arm_max = int(input('\nInput points of Spirit Armour as an integer:'))
                        except ValueError:
                            print("\nInvalid value, Spirit Armour not changed.")
                        try:
                            editchar.glob_magic_arm_max = int(input('\nInput points of Magic Armour as an integer:'))
                        except ValueError:
                            print("\nInvalid value, Magic Armour not changed.")
                        try:
                            editchar.glob_dac_max = int(input('\nInput points of DAC as an integer:'))
                        except ValueError:
                            print("\nInvalid value, DAC not changed.")

                    # Edit resources
                    elif edit_choice == "4":
                        print('Spirit points: ' + str(editchar.spirit_points_max))
                        print('Mana points : ' + str(editchar.mana_points_max))
                        try:
                            editchar.spirit_points_max = int(input('\nInput points of Spirit as an integer:'))
                        except ValueError:
                            print("\nInvalid value, Spirit points not changed.")
                        try:
                            editchar.mana_points_max = int(input('\nInput points of Mana as an integer:'))
                        except ValueError:
                            print("\nInvalid value, Mana points not changed.")
                    
                    # Edit character weapon
                    elif edit_choice == "5":
                        print('Current Weapons : ' + str([o.name for o in editchar.weapons]))
                        print('\nWIP - Choose a single character weapon:')
                        print('\nChoose a weapon:')
                        for x in range(len(weapon_select)):
                            print(str(x+1) + ' - ' + weapon_select[x].name + ',')
                        try: 
                            char_weapon_select = int(input('\nChoice:'))
                            if char_weapon_select-1 in range(len(weapon_select)):
                                editchar.weapons = [weapon_select[char_weapon_select-1]]
                            else:
                                raise ValueError
                        except ValueError:
                            print("\nInvalid value, weapon not changed")

                    #Edit character ability
                    elif edit_choice == "6":
                        print('Current Abilities :' + str([o.name for o in editchar.abilities])) 
                        print('\nWIP - Choose a single character ability:')
                        print('0 - No Abilities')
                        for x in range(len(ability_select)):
                            print(str(x+1) + ' - ' + ability_select[x].name + ',')
                        try: 
                            char_ability_select = int(input('\nChoice:'))
                            if char_ability_select == 0:
                                editchar.abilities = []
                            elif char_ability_select-1 not in range(len(ability_select)):
                                raise ValueError
                            else:
                                editchar.abilities = [ability_select[char_ability_select-1]]
                        except ValueError:
                            print("\nInvalid value, abilities not changed")

                    else:
                        print("\nInvalid choice.")

        # Delete character
        elif choice == "3":
            chardel = input("Which character would you like to delete?: ")
            chardelCap = chardel.capitalize()
            if chardelCap not in character_list:
                print("\nCharacter does not exist.")
            else:
                areusure = input("\nAre you sure you want to delete this character? 'Y' for YES, 'N' for NO: ")
                areusureCap = areusure.upper()
                if areusureCap == "Y":
                    del character_list[chardelCap]
                    print("\nCharacter WAS deleted.")
                else:
                    print("\nCharacter NOT deleted.")

        # List characters
        elif choice == "4":
            if character_list:
                for key in character_list:
                    print(key)
                    print(character_list.get(key))
            else:
                print("\nNo characters found")

        # Save characters
        elif choice == "5":
            # Save characters to file
            print("\nSaving...")
            with open('characters.txt','w') as outfile:
                outfile.write(jsonpickle.encode(character_list))
            print("\nSaving complete.")

        # Load characters
        # Issue - What we load back in just becomes a dictionary object...
        elif choice == "6":
            # Load characters from file
            print("\Loading...")
            with open('characters.txt','r') as infile:
                character_list = jsonpickle.decode(infile.read())
            print("\nLoading complete.")

        else:
            print("\nInvalid choice.")

    #Should probably prompt to save before quitting
    print("Exiting...")

if __name__ == "__main__":
    main()