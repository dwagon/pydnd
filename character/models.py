from django.db import models
import random


##############################################################################
def dice(sides=6):
    return random.randint(1, sides)


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
class Spell(models.Model):
    name = models.CharField(max_length=200)
    level = models.IntegerField()


alignment_choices = (
        ('LG', 'Lawful Good'), ('LN', 'Lawful Neutral'), ('LE', 'Lawful Evil'),
        ('NG', 'Neutral Good'), ('N', 'True Neutral'), ('NE', 'Neutral Evil'),
        ('CG', 'Chaotic Good'), ('CN', 'Chaotic Neutral'), ('CE', 'Chaotic Evil')
        )
race_choices = (
        ('HU', 'Human'),
        ('EL', 'Elf'),
        ('DW', 'Dwarf'),
        ('HE', 'Half Elven'),
        ('HL', 'Halfling')
        )
status_choices = (
        ('OK', 'OK'),
        ('DE', 'Dead'),
        ('UC', 'Unconscious')
        )
gender_choices = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('U', 'Unknown')
        )


##############################################################################
class Character(models.Model):
    name = models.CharField(max_length=200)
    race = models.CharField(max_length=2, choices=race_choices, default='HU')
    gender = models.CharField(max_length=1, choices=gender_choices, default='U')
    hp = models.IntegerField(default=0)
    max_hp = models.IntegerField(default=0)
    ac = models.IntegerField(default=10)
    thaco = models.IntegerField(default=0)
    dmg = models.IntegerField(default=1)
    encumbrance = models.IntegerField(default=0)
    movement = models.IntegerField(default=6)
    xp = models.IntegerField(default=0)
    align = models.CharField(max_length=2, choices=alignment_choices, default='N')
    level = models.IntegerField(default=1)
    status = models.CharField(max_length=2, choices=status_choices, default='OK')

    stat_str = models.IntegerField(default=-1)
    bonus_str = models.IntegerField(default=-1)
    stat_int = models.IntegerField(default=-1)
    stat_wis = models.IntegerField(default=-1)
    stat_dex = models.IntegerField(default=-1)
    stat_con = models.IntegerField(default=-1)
    stat_cha = models.IntegerField(default=-1)

    plat = models.IntegerField(default=0)
    gold = models.IntegerField(default=0)
    silver = models.IntegerField(default=0)
    copper = models.IntegerField(default=0)

    gear = models.ManyToManyField(Equipment, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return "{} Level {} {}".format(self.name, self.level, self.__class__.__name__)

    def generate_stats(self):
        self.stat_str = self.roll_stat()
        if self.stat_str == 18:
            self.bonus_str = random.randint(1, 100)
        self.stat_dex = self.roll_stat()
        self.stat_int = self.roll_stat()
        self.stat_con = self.roll_stat()
        self.stat_wis = self.roll_stat()
        self.stat_cha = self.roll_stat()

    def save(self, **kwargs):
        if self.stat_str < 0:
            self.generate_stats()
        if self.max_hp == 0:
            self.max_hp = dice(self.hitdie)
            self.hp = self.max_hp
        self.encumbrance = self.calc_encumb()

        super(Character, self).save(**kwargs)

    def calc_encumb(self):
        enc = sum(x.weight for x in self.gear.all())
        return enc

    def roll_stat(self):
        """ Roll 4d6 and return the sum of the top 3
        Method VI in the PHG
        """
        return sum(sorted([dice(), dice(), dice(), dice()])[1:])


##############################################################################
class Thief(Character):
    hitdie = 6

    class Meta:
        verbose_name_plural = "Thieves"


##############################################################################
class Fighter(Character):
    hitdie = 10


##############################################################################
class Mage(Character):
    spells = models.ManyToManyField(Spell)
    hitdie = 4


##############################################################################
class Cleric(Character):
    spells = models.ManyToManyField(Spell, blank=True)
    hitdie = 6

# EOF
