from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from character.models import Character
# from monster.models import Monster
from monster.models import MonsterState
from encounter.models import Encounter


##############################################################################
class World(models.Model):
    name = models.CharField(max_length=200, unique=True)

    ##########################################################################
    def all_pcs(self):
        return Character.objects.filter(world=self)

    ##########################################################################
    def all_monsters(self):
        return MonsterState.objects.filter(world=self)

    ##########################################################################
    def __getitem__(self, loc):
        enc = Encounter.objects.filter(world=self)[0]
        try:
            loc = enc.locations.get(x=loc[0], y=loc[1])
            return loc.content_object
        except ObjectDoesNotExist:
            return None

# EOF
