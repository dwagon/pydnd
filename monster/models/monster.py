from django.db import models

alignment_choices = (
        ('LG', 'Lawful Good'), ('LN', 'Lawful Neutral'), ('LE', 'Lawful Evil'),
        ('NG', 'Neutral Good'), ('N', 'True Neutral'), ('NE', 'Neutral Evil'),
        ('CG', 'Chaotic Good'), ('CN', 'Chaotic Neutral'), ('CE', 'Chaotic Evil')
        )


##############################################################################
class Monster(models.Model):
    name = models.CharField(max_length=200)
    treasure = models.CharField(max_length=50)
    align = models.CharField(max_length=2, choices=alignment_choices, default='N')
    numappearing = models.CharField('Num Appearing', max_length=20)
    ac = models.IntegerField('AC')
    movement = models.IntegerField()
    hitdie = models.CharField('Hit Die', max_length=5)
    thaco = models.IntegerField()
    numattacks = models.IntegerField('Num Attacks', default=1)
    damage = models.CharField(max_length=5)
    xp = models.IntegerField()

    def __str__(self):
        return self.name

# EOF
