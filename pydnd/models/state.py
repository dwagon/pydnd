from django.db import models
import status


##############################################################################
class CreatureState(models.Model):
    hp = models.IntegerField(default=0)
    max_hp = models.IntegerField(default=0)
    status = models.CharField(max_length=2, choices=status.status_choices, default=status.UNDEF)
    x = models.IntegerField(default=-1)
    y = models.IntegerField(default=-1)
    initseq = models.IntegerField(default=-1)
    moves = models.IntegerField(default=-1)

    class Meta(object):
        abstract = True

# EOF
