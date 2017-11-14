from django.db import models
from utils import roll


##############################################################################
class Equipment(models.Model):
    name = models.CharField(max_length=200)
    cost = models.IntegerField(default=0)    # Cost in CP
    weight = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Equipment"

    def __str__(self):
        return self.name


##############################################################################
class Weapons(Equipment):
    damage = models.CharField(max_length=10)
    magic = models.CharField(max_length=10, default='')

    def hit(self):
        return roll('{} {}'.format(self.damage, self.magic))


##############################################################################
class Armour(Equipment):
    ac_base = models.IntegerField(default=0)
    ac_modifier = models.IntegerField(default=0)
    magic = models.CharField(max_length=10, default='')


# EOF
