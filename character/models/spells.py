from django.db import models


##############################################################################
class Spell(models.Model):
    name = models.CharField(max_length=200)
    level = models.IntegerField()


# EOF
