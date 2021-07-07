# Special abilities module

# Setup a class for special abilities
class Ability:
    'Base Class that defines abilities which affect combat'
    type = None
    def __init__(self,name,target,speed,resource_activate,resource_cost):
        self.name,self.target,self.speed,self.resource_activate,self.resource_cost = name,target,speed,resource_activate,resource_cost

class AbilityGrantStatus(Ability):
    'Class that defines abilities which apply a status effect'
    type = 'abilitygrantstatus'
    def __init__(self,name,target,speed,resource_activate,resource_cost,associated_status,associated_status_duration):
        super().__init__(name,target,speed,resource_activate,resource_cost)
        self.associated_status,self.associated_status_duration = associated_status,associated_status_duration

class AbilityDamageDirect(Ability):
    'Class that defines abilities which damage directly damage a creature'
    type = 'abilitydamagedirect'
    # This is the TT equivalent of a "THREE" as opposed to a "TRIPLE"
    # Note : Damage types not implemented
    def __init__(self,name,target,speed,resource_activate,resource_cost,damage):
        super().__init__(name,target,speed,resource_activate,resource_cost)
        self.damage = damage

class AbilityHealCreature(Ability):
    'Class that defines abilities which heal creatures'
    type = 'abilityhealcreature'
    # Note : This only supports immediate numerical healing abilities, it doesn't support "heal sufficient" or "lay on hands" miracles
    def __init__(self,name,target,speed,resource_activate,resource_cost,healing):
        super().__init__(name,target,speed,resource_activate,resource_cost)
        self.healing = healing

class AbilityAffectCreature(Ability):
    'Class that defines abilities which directly modify non-hit point creature attributes'
    type = 'abilityaffectcreature'
    def __init__(self,name,target,speed,resource_activate,resource_cost,attribute_target,attribute_mod):
        super().__init__(name,target,speed,resource_activate,resource_cost)
        self.attribute_target,self.attribute_mod = attribute_target,attribute_mod