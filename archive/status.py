# Status class module

# Setup a class for statuses
class Status:
    'Class that defines statuses which affect combat'

    def __init__(self,name,status_rating_multi=1,status_hit_multi=[1,1,1,1,1,1],status_damage_mod=0,status_damage_multi=1):
        self.name,self.status_rating_multi,self.status_hit_multi = name,status_rating_multi,status_hit_multi
        self.status_damage_mod,self.status_damage_multi = status_damage_mod,status_damage_multi