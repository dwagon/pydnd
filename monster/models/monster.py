from django.db import models
from constants import size_choices
from pydnd.models import Creature


##############################################################################
class Monster(Creature):
    size = models.CharField(max_length=2, choices=size_choices, default='M')
    hitdie = models.CharField('Hit Die', max_length=10, default='1d8')
    dmg_vuln = models.CharField(max_length=200, default="")
    dmg_immun = models.CharField(max_length=200, default="")
    cond_immun = models.CharField(max_length=200, default="")
    challenge = models.CharField(max_length=10)

    ##########################################################################
    def __str__(self):
        return self.name

# EOF
