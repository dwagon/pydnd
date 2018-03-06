from django.db import models


##############################################################################
class Equipment(models.Model):
    name = models.CharField(max_length=200)
    cost = models.CharField(max_length=20)
    weight = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Equipment"

# EOF
