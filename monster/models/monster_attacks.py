from django.db import models
from lib.constants import damage_cat_choices


##############################################################################
class MonsterAttacks(models.Model):
    monster = models.ForeignKey('Monster', on_delete=models.CASCADE)
    name = models.CharField(max_length=200, unique=True)
    desc = models.CharField(max_length=200, unique=True)
    to_hit = models.IntegerField()
    reach = models.IntegerField()
    damage = models.CharField(max_length=10)
    damage_cat = models.CharField(max_length=2, choices=damage_cat_choices)
    normal_range = models.IntegerField(default=0)
    long_range = models.IntegerField(default=0)


# EOF
