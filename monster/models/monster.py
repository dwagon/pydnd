from django.db import models
from constants import alignment_choices, size_choices


##############################################################################
class Monster(models.Model):
    name = models.CharField(max_length=200, unique=True)
    align = models.CharField(max_length=2, choices=alignment_choices, default='N')
    size = models.CharField(max_length=2, choices=size_choices, default='M')
    ac = models.IntegerField('AC', default=10)
    hitdie = models.CharField('Hit Die', max_length=10, default='1d8')
    speed = models.IntegerField(default=30)
    stat_str = models.IntegerField(default=-1)
    stat_int = models.IntegerField(default=-1)
    stat_wis = models.IntegerField(default=-1)
    stat_dex = models.IntegerField(default=-1)
    stat_con = models.IntegerField(default=-1)
    stat_cha = models.IntegerField(default=-1)
    dmg_vuln = models.CharField(max_length=200, default="")
    dmg_immun = models.CharField(max_length=200, default="")
    cond_immun = models.CharField(max_length=200, default="")
    challenge = models.CharField(max_length=10)

    ##########################################################################
    def __str__(self):
        return self.name

# EOF
