from django.db import models
import random
from . import tables
from utils import roll


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
        ('HL', 'Halfling'),
        ('GN', 'Gnome')
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
charclass_choices = (
        ('F', 'Fighter'),
        ('T', 'Thief'),
        ('M', 'Mage'),
        ('C', 'Cleric'),
        )


##############################################################################
class EquipState(models.Model):
    character = models.ForeignKey('Character', on_delete=models.CASCADE)
    equipment = models.ForeignKey('Equipment', on_delete=models.CASCADE)
    ready = models.BooleanField(default=False)


##############################################################################
class SpellState(models.Model):
    character = models.ForeignKey('Character', on_delete=models.CASCADE)
    spell = models.ForeignKey('Spell', on_delete=models.CASCADE)
    memorized = models.BooleanField(default=False)
    default = models.BooleanField(default=False)


##############################################################################
class Character(models.Model):
    name = models.CharField(max_length=200)
    charclass = models.CharField(max_length=5, choices=charclass_choices)
    race = models.CharField(max_length=2, choices=race_choices, default='HU')
    gender = models.CharField(max_length=1, choices=gender_choices, default='U')
    hp = models.IntegerField(default=0)
    max_hp = models.IntegerField(default=0)
    ac = models.IntegerField(default=10)
    thaco = models.IntegerField(default=0)
    dmg = models.IntegerField(default=1)
    encumbrance = models.IntegerField(default=0)
    movement = models.IntegerField(default=12)
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

    gear = models.ManyToManyField('Equipment', blank=True, through=EquipState)
    spells = models.ManyToManyField('Spell', blank=True, through=SpellState)

    def __str__(self):
        return "{} (Level {} {})".format(self.name, self.level, self.get_charclass_display())

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
            self.max_hp = self.calc_hp()
            self.hp = self.max_hp
        # Need to save first to make M2M work on new objects
        super(Character, self).save(**kwargs)
        self.encumbrance = self.calc_encumb()
        self.movement = self.calc_movement()
        self.thaco = self.calc_thaco()
        super(Character, self).save(**kwargs)

    def calc_movement(self):
        # TODO: Encumbrance
        return tables.race[self.race]['movement']

    def calc_hp(self):
        """ Calculate the HP for a level - try and make it not suck too much """
        if self.charclass == 'F':
            index = 1
        else:
            index = 0
        return max(roll(self.hitdie()), roll(self.hitdie())) + tables.con_hp_adjustment[self.stat_con][index]

    def calc_encumb(self):
        enc = sum(x.weight for x in self.gear.all())
        return enc

    def roll_stat(self):
        """ Roll 4d6 and return the sum of the top 3
        Method VI in the PHG
        """
        return sum(sorted([roll('d6'), roll('d6'), roll('d6'), roll('d6')])[1:])

    def equip(self, obj, ready=False):
        e = EquipState(character=self, equipment=obj, ready=ready)
        e.save()

    def equipped_weapon(self):
        """ Return the equiped weapon """
        e = self.gear.filter(equipstate__ready=True)
        for _ in e:
            if _.get_category_display() == 'Weapon':
                return _
        return None

    def hit(self, victim):
        hitroll = roll('d20')
        to_hit = self.thaco - victim.ac
        print("hitroll={} to_hit={} thaco={} AC={}".format(hitroll, to_hit, self.thaco, victim.ac))
        self.equipped_weapon()
        if hitroll > to_hit:
            return True
        else:
            return False

    def attack(self, victim):
        weap = self.equipped_weapon()
        print("Weapon={}".format(weap))
        if self.hit(victim):
            print("hit!")
            # Calc Damage
            # victim.hurt(dmg)
        else:
            print("Missed")

    def calc_thaco(self):
        if self.charclass == 'T':
            return 20 - int((self.level - 1) / 2)
        elif self.charclass == 'F':
            return 21 - self.level
        elif self.charclass == 'M':
            return 20 - int((self.level - 1) / 3)
        elif self.charclass == 'C':
            return 20 - int((self.level - 1) * 2 / 3)

    def hitdie(self):
        if self.charclass == 'T':
            return 'd6'
        elif self.charclass == 'F':
            return 'd10'
        elif self.charclass == 'M':
            return 'd4'
        elif self.charclass == 'C':
            return 'd8'

# EOF
