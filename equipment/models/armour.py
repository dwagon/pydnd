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

    def calc_ac(self, dexmod):
        if self.armour_categ == 'L':
            return self.base_ac + dexmod
        elif self.armour_categ == 'M':
            return self.base_ac + min(dexmod, 2)
        elif self.armour_categ == 'H':
            return self.base_ac
        elif self.armour_categ == 'S':
            return 2

# EOF
