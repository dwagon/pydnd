from django.db import models


##############################################################################
class Wall(models.Model):
    x = models.IntegerField(default=-1)
    y = models.IntegerField(default=-1)

    name = "Wall"

    def __str__(self):
        return "Wall at {}, {}".format(self.x, self.y)

# EOF
