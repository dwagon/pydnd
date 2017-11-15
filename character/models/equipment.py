from django.db import models
from utils import roll




##############################################################################
def Weapon(**kwargs):
    return Equipment(category='W', **kwargs)


##############################################################################
def Armour(**kwargs):
    return Equipment(category='A', **kwargs)


##############################################################################
class Equipment(models.Model):
    ITEM = 'I'
    WEAPON = 'W'
    ARMOUR = 'A'
    category_choices = (
            (ITEM, 'Item'),
            (WEAPON, 'Weapon'),
            (ARMOUR, 'Armour')
            )
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=1, choices=category_choices, default=ITEM)
    cost = models.IntegerField(default=0)    # Cost in CP
    weight = models.IntegerField(default=0)
    magic = models.CharField(max_length=10, default='')

    # Weapon stuff
    damage = models.CharField(max_length=10, default='')

    # Armour stuff
    ac_base = models.IntegerField(default=10)
    ac_modifier = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Equipment"

    def __str__(self):
        return "{} {}".format(self.get_category_display(), self.name)

    def weapon_dmg(self):
        return roll('{} {}'.format(self.damage, self.magic))

# EOF
