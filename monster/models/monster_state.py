from django.db import models
from utils import roll
import status


##############################################################################
class MonsterState(models.Model):
    name = models.CharField(max_length=200, default="", blank=True)
    encounter = models.ForeignKey('encounter.Encounter', on_delete=models.CASCADE, related_name='monsters')
    monster = models.ForeignKey('Monster', on_delete=models.CASCADE)
    hp = models.IntegerField(default=-1)
    max_hp = models.IntegerField(default=-1)
    status = models.CharField(max_length=2, choices=status.status_choices, default=status.UNDEF)
    x = models.IntegerField(default=-1)
    y = models.IntegerField(default=-1)
    moves = models.IntegerField(default=-1)
    initiative = models.IntegerField(default=-1)
    attacks = models.IntegerField(default=-1)

    animate = True

    ##########################################################################
    def save(self, **kwargs):
        if self.status == status.UNDEF:
            self.status = status.OK
            hits = roll(self.monster.hitdie)
            self.max_hp = hits
            self.hp = hits
        super(MonsterState, self).save(**kwargs)

    ##########################################################################
    def __str__(self):
        name = self.name if self.name else self.monster.name
        return "{} {} (HP:{}/{})".format(name, self.get_status_display(), self.hp, self.max_hp)

    ##########################################################################
    def hurt(self, dmg, dmg_cat):
        """ Be hurt """
        self.hp -= dmg
        if self.hp <= 0:
            self.status = status.DEAD
            self.save()
            return False
        return True

    ##########################################################################
    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError("AttrError on {}".format(name))
        return getattr(self.monster, name)

    ##########################################################################
    def get_reach(self):
        return self.reach

    ##########################################################################
    def start_turn(self):
        self.generate_initiative()
        self.moves = self.speed
        self.save()

    ##########################################################################
    def generate_initiative(self):
        init = roll('d10')
        self.initiative = init
        self.save()
        return init

# EOF
