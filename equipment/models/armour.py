from django.db import models
from .equipment import Equipment


##############################################################################
class Armour(Equipment):
    LIGHT = 'L'
    MEDIUM = 'M'
    HEAVY = 'H'
    armour_choices = (
        (LIGHT, 'Light'),
        (MEDIUM, 'Medium'),
        (HEAVY, 'Heavy')
        )
    stealth_disadv = models.BooleanField(default=False)
    base_ac = models.IntegerField(default=-1)
    armour_categ = models.CharField(max_length=1, choices=armour_choices)

    def calc_ac(self):
        pass
