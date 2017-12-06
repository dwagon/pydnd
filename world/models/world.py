from django.db import models
from character.models import Character
# from monster.models import Monster
from monster.models import MonsterState
# from encounter.models import Encounter


##############################################################################
class World(models.Model):
    pass

    def all_pcs(self):
        return Character.objects.filter(world=self)

    def all_monsters(self):
        return MonsterState.objects.filter(world=self)


# EOF
