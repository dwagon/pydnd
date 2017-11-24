from django.db import models
from utils import roll
from constants import alignment_choices


##############################################################################
class MonsterState(models.Model):
    OK = 'OK'
    DEAD = 'DE'
    UNCONSCIOUS = 'UC'
    UNDEF = 'XX'
    status_choices = (
        (OK, 'OK'),
        (DEAD, 'Dead'),
        (UNCONSCIOUS, 'Unconscious')
        )

    monster = models.ForeignKey('Monster', on_delete=models.CASCADE)
    hp = models.IntegerField(default=-1)
    max_hp = models.IntegerField(default=-1)
    status = models.CharField(max_length=2, choices=status_choices, default=UNDEF)
    x = models.IntegerField(default=-1)
    y = models.IntegerField(default=-1)

    def save(self, **kwargs):
        if self.status == self.UNDEF:
            self.status = self.OK
            hits = roll(self.monster.hitdie)
            self.max_hp = hits
            self.hp = hits
        super(MonsterState, self).save(**kwargs)

    def __str__(self):
        return "{} {} (HP:{}/{})".format(self.monster.name, self.get_status_display(), self.hp, self.max_hp)

    def hurt(self, dmg):
        """ Be hurt """
        self.hp -= dmg
        if self.hp <= 0:
            self.status = self.DEAD
            self.save()
            return False
        return True

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError("AttrError on {}".format(name))
        return getattr(self.monster, name)

    def get_reach(self):
        return self.reach


##############################################################################
class Monster(models.Model):
    name = models.CharField(max_length=200, unique=True)
    treasure = models.CharField(max_length=50)
    align = models.CharField(max_length=2, choices=alignment_choices, default='N')
    numappearing = models.CharField('Num Appearing', max_length=20)
    ac = models.IntegerField('AC')
    movement = models.IntegerField(default=9)
    hitdie = models.CharField('Hit Die', max_length=5, default='1d8')
    thaco = models.IntegerField()
    numattacks = models.IntegerField('Num Attacks', default=1)
    damage = models.CharField(max_length=50)
    xp = models.IntegerField()
    reach = models.IntegerField(default=0)

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

# EOF
