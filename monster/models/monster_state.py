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
    def start_turn(self):
        self.moves = self.speed
        self.save()

    ##########################################################################
    def in_range(self, dist):
        attacks = self.attacks.all()
        for att in attacks:
            if att.in_range(dist):
                return True
        return False

    ##########################################################################
    def take_action(self, encounter):
        """ Default monster action - need to override later """
        targ = encounter.nearest_enemy(self)
        if targ:
            dist = encounter.distance(self, targ)
            if targ.in_range(dist):
                dmgs = self.attack(targ)
                targ.hurt(dmgs)
                return
        self.move(encounter, targ)

    ##########################################################################
    def attack(self, victim):
        """ Attack something else """
        dmgs = []
        dist = self.victim.encounter.distance(self, victim)
        for att in self.attacks.all():
            if att.in_range(dist):
                dmg = self.attack_with(victim, att)
                if dmg:
                    dmgs.append(dmg)
                break
        return dmgs

    ##########################################################################
    def initiative(self):
        init = roll('d20') + self.stat_bonus(self.stat_dex)
        return init

    ##########################################################################
    def attack_with(self, victim, weapon):
        if weapon.hit(victim.ac):
            return weapon.dmg()
        return None

# EOF
