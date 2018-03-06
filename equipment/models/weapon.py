from django.db import models
from .equipment import Equipment


##############################################################################
class Weapon(Equipment):
    BLUDGEONING = 'B'
    SLASHING = 'S'
    PIERCING = 'P'
    damage_cat_choices = (
        (BLUDGEONING, 'Bludgeoning'),
        (SLASHING, 'Slashing'),
        (PIERCING, 'Piercing'),
        )
    damage = models.CharField(max_length=10)
    damage_cat = models.CharField(max_length=2, choices=damage_cat_choices)
    properties = models.CharField(max_length=50)
    normal_range = models.IntegerField(default=0)
    long_range = models.IntegerField(default=0)

# EOF
