# Weapon class module

# Setup a class for weapons
class Weapon:
    'Class that defines weapons which affect combat'

    def __init__(self,name,weapon_rating_mod,weapon_hit_mod):
        self.name,self.weapon_rating_mod,self.weapon_hit_mod = name,weapon_rating_mod,weapon_hit_mod