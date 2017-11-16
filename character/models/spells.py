from django.db import models


##############################################################################
class Spell(models.Model):
    name = models.CharField(max_length=200)
    level = models.IntegerField()

    def __str__(self):
        return "{} (Level {})".format(self.name, self.level)


# EOF
