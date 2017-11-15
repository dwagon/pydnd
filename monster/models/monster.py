from django.db import models
from utils import roll

alignment_choices = (
        ('LG', 'Lawful Good'), ('LN', 'Lawful Neutral'), ('LE', 'Lawful Evil'),
        ('NG', 'Neutral Good'), ('N', 'True Neutral'), ('NE', 'Neutral Evil'),
        ('CG', 'Chaotic Good'), ('CN', 'Chaotic Neutral'), ('CE', 'Chaotic Evil')
        )
status_choices = (
        ('OK', 'OK'),
        ('DE', 'Dead'),
        ('UC', 'Unconscious')
        )


##############################################################################
class Monster(models.Model):
    name = models.CharField(max_length=200)
    treasure = models.CharField(max_length=50)
    align = models.CharField(max_length=2, choices=alignment_choices, default='N')
    numappearing = models.CharField('Num Appearing', max_length=20)
    ac = models.IntegerField('AC')
    movement = models.IntegerField()
    hitdie = models.CharField('Hit Die', max_length=5, default='1')
    thaco = models.IntegerField()
    numattacks = models.IntegerField('Num Attacks', default=1)
    damage = models.CharField(max_length=5)
    xp = models.IntegerField()
    hp = models.IntegerField(default=-1)
    max_hp = models.IntegerField(default=-1)
    status = models.CharField(max_length=2, choices=status_choices, default='OK')

    def save(self, **kwargs):
        if self.max_hp < 0:
            hits = roll('{}d8'.format(self.hitdie))
            self.max_hp = hits
            self.hp = hits
        super(Monster, self).save(**kwargs)

    def __str__(self):
        return self.name

    def attack(self, victim):
        """ Attack something else """
        dmgs = 0
        for _ in range(0, self.numattacks):
            if self.hit(victim):
                dmg = roll(self.damage)
                victim.hurt(dmg)
                dmgs += dmg
        return dmgs

    def hit(self, victim):
        """ Try and hit something """
        hitroll = roll('d20')
        to_hit = self.thaco - victim.ac
        if hitroll >= to_hit:
            return True
        else:
            return False

    def hurt(self, dmg):
        """ Be hurt """
        self.hp -= dmg
        if self.hp <= 0:
            self.status = 'DE'
            self.save()
            return False
        return True

# EOF
