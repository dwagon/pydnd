from django.db import models
from lib.constants import damage_cat_choices
from utils import roll


##############################################################################
class MonsterAttack(models.Model):
    monster = models.ForeignKey('Monster', on_delete=models.CASCADE, related_name='attacks')
    name = models.CharField(max_length=200, unique=True)
    desc = models.CharField(max_length=200, unique=True)
    to_hit = models.IntegerField()
    reach = models.IntegerField()
    damage = models.CharField(max_length=10)
    damage_cat = models.CharField(max_length=2, choices=damage_cat_choices)
    normal_range = models.IntegerField(default=0)
    long_range = models.IntegerField(default=0)

    ##########################################################################
    def in_range(self, distance):
        if distance < self.reach:
            return True
        if distance < self.long_range:
            return True
        return False

    ##########################################################################
    def __str__(self):
        return "{} {} ({})".format(self.monster.name, self.name, self.desc)

    ##########################################################################
    def hit(self, ac):
        hitroll = roll('d20') + self.to_hit
        if hitroll > ac:
            return True
        else:
            return False

    ##########################################################################
    def dmg(self):
        damage = roll(self.damage)
        return (damage, self.damage_cat)

# EOF
