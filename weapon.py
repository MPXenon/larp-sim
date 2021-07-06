# Weapon class module

# Setup a class for weapons
class Weapon:
    'Class that defines weapons which affect combat'

    def __init__(self,name,weapon_rating_multi,weapon_hit_multi):
        self.name,self.weapon_rating_multi,self.weapon_hit_multi = name,weapon_rating_multi,weapon_hit_multi