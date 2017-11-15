from django.db import models
from utils import roll


category_choices = (
        ('I', 'Item'),
        ('W', 'Weapon'),
        ('A', 'Armour')
        )


##############################################################################
def Weapon(**kwargs):
    return Equipment(category='W', **kwargs)


##############################################################################
def Armour(**kwargs):
    return Equipment(category='A', **kwargs)


##############################################################################
class Equipment(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=1, choices=category_choices, default='I')
    cost = models.IntegerField(default=0)    # Cost in CP
    weight = models.IntegerField(default=0)
    magic = models.CharField(max_length=10, default='')

    # Weapon stuff
    damage = models.CharField(max_length=10, default='')

    # Armour stuff
    ac_base = models.IntegerField(default=0)
    ac_modifier = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Equipment"

    def __str__(self):
        return "{} {}".format(self.get_category_display(), self.name)

    def weapon_dmg(self):
        return roll('{} {}'.format(self.damage, self.magic))

# EOF
