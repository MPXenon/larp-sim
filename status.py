# Status class module

# Setup a class for statuses
class Status:
    'Class that defines statuses which affect combat'

    def __init__(self,name,status_rating_mod,status_hit_mod):
        self.name,self.status_rating_mod,self.status_hit_mod = name,status_rating_mod,status_hit_mod
