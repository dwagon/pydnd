from django.db import models
from character.models import Character
# from monster.models import Monster
from monster.models import MonsterState
# from encounter.models import Encounter


##############################################################################
class World(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def all_pcs(self):
        return Character.objects.filter(world=self)

    def all_monsters(self):
        return MonsterState.objects.filter(world=self)


# EOF
