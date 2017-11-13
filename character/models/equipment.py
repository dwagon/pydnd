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

# EOF
