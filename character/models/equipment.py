from django.db import models


##############################################################################
class Equipment(models.Model):
    name = models.CharField(max_length=200)
    cost = models.IntegerField()    # Cost in CP
    weight = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Equipment"

    def __str__(self):
        return self.name


##############################################################################
class Weapons(Equipment):
    damage = models.CharField(max_length=10)
    magic = models.IntegerField(default=0)


##############################################################################
class Armour(Equipment):
    bonus = models.IntegerField()
    magic = models.IntegerField(default=0)


# EOF
