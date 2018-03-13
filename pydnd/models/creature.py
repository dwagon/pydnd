from django.db import models
from constants import alignment_choices


##############################################################################
class Creature(models.Model):
    name = models.CharField(max_length=200, default='')
    align = models.CharField(max_length=2, choices=alignment_choices, default='N')
    ac = models.IntegerField(default=10)
    speed = models.IntegerField(default=30)
    stat_str = models.IntegerField(default=-1)
    stat_int = models.IntegerField(default=-1)
    stat_wis = models.IntegerField(default=-1)
    stat_dex = models.IntegerField(default=-1)
    stat_con = models.IntegerField(default=-1)
    stat_cha = models.IntegerField(default=-1)

    class Meta(object):
        abstract = True

    ##########################################################################
    def stat_bonus(self, stat):
        mod = int(stat - 10) / 2
        return mod

# EOF
