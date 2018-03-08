from django.db import models
from .equipment import Equipment
from lib.constants import damage_cat_choices


##############################################################################
class Weapon(Equipment):
    damage = models.CharField(max_length=10)
    damage_cat = models.CharField(max_length=2, choices=damage_cat_choices)
    properties = models.CharField(max_length=50, default='')
    normal_range = models.IntegerField(default=0)
    long_range = models.IntegerField(default=0)

# EOF
