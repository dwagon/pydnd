from django.db import models
from .equipment import Equipment


##############################################################################
class Armour(Equipment):
    LIGHT = 'L'
    MEDIUM = 'M'
    HEAVY = 'H'
    SHIELD = 'S'
    armour_choices = (
        (LIGHT, 'Light'),
        (MEDIUM, 'Medium'),
        (HEAVY, 'Heavy'),
        (SHIELD, 'Shield')
        )
    stealth_disadv = models.BooleanField(default=False)
    base_ac = models.IntegerField(default=-1)
    armour_categ = models.CharField(max_length=1, choices=armour_choices)

    def calc_ac(self):
        pass
