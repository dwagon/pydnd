from django.db import models
import random


class Equipment(models.Model):
    name = models.CharField(max_length=200)
    cost = models.IntegerField()


class Spell(models.Model):
    name = models.CharField(max_length=200)
    level = models.IntegerField()


class Character(models.Model):
    name = models.CharField(max_length=200)
    char_class = models.CharField(max_length=200)
    race = models.CharField(max_length=200)
    hp = models.IntegerField()
    xp = models.IntegerField()
    level = models.IntegerField()
    spells = models.ManyToManyField(Spell)

    stat_str = models.IntegerField()
    bonus_str = models.IntegerField(default=0)
    stat_dex = models.IntegerField()
    stat_int = models.IntegerField()
    stat_con = models.IntegerField()
    stat_wis = models.IntegerField()
    stat_cha = models.IntegerField()

    plat = models.IntegerField()
    gold = models.IntegerField()
    silver = models.IntegerField()
    copper = models.IntegerField()

    gear = models.ManyToManyField(Equipment)

    def roll_stats(self):
        self.stat_str = self.td6()
        if self.stat_str == 18:
            self.bonus_str = random.randint(1, 100)
        self.stat_dex = self.td6()
        self.stat_int = self.td6()
        self.stat_con = self.td6()
        self.stat_wis = self.td6()
        self.stat_cha = self.td6()

    def td6(self):
        return self.d6() + self.d6() + self.d6()

    def d6(self):
        return random.randint(1, 6)

# EOF
