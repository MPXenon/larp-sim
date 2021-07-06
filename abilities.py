# Special abilities module

# Setup a class for special abilities
class Ability:
    'Class that defines abilities which affect combat'
    # These should really be AbilityGrantStatus
    def __init__(self,name,target,speed,resource_activate,resource_cost,associated_status,associated_status_duration):
        self.name,self.target,self.speed,self.resource_activate,self.resource_cost = name,target,speed,resource_activate,resource_cost
        self.associated_status,self.associated_status_duration = associated_status,associated_status_duration
    # Notes : Might want to add a target - self, friendly, hostile, touch/on_hit

# Will also want AbilityImmediates or AbilityAffectCreature or something similar to handle Magic Armour, Healing etc.