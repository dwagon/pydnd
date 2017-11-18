from django.db import models
import random
from . import tables
from . import Equipment, Spell
from world.models import World
from utils import roll
from constants import alignment_choices


##############################################################################
class EquipState(models.Model):
    character = models.ForeignKey('Character', on_delete=models.CASCADE)
    equipment = models.ForeignKey('Equipment', on_delete=models.CASCADE)
    ready = models.BooleanField(default=False)

    def __str__(self):
        return "{}'s {}".format(self.character.name, self.equipment.name)


##############################################################################
class SpellState(models.Model):
    character = models.ForeignKey('Character', on_delete=models.CASCADE)
    spell = models.ForeignKey(Spell, on_delete=models.CASCADE)
    memorized = models.BooleanField(default=False)
    default = models.BooleanField(default=False)

    def __str__(self):
        memstr = ""
        if self.memorized:
            memstr = "memorized "
        return "{}'s {}{}".format(self.character.name, memstr, self.spell.name)


##############################################################################
def Fighter(**kwargs):
    return Character(charclass=Character.FIGHTER, **kwargs)


##############################################################################
def Thief(**kwargs):
    return Character(charclass=Character.THIEF, **kwargs)


##############################################################################
def Mage(**kwargs):
    return Character(charclass=Character.MAGE, **kwargs)


##############################################################################
def Cleric(**kwargs):
    return Character(charclass=Character.CLERIC, **kwargs)


##############################################################################
class Character(models.Model):
    # Character Class Choices
    FIGHTER = 'F'
    THIEF = 'T'
    MAGE = 'M'
    CLERIC = 'C'
    charclass_choices = (
        (FIGHTER, 'Fighter'),
        (THIEF, 'Thief'),
        (MAGE, 'Mage'),
        (CLERIC, 'Cleric'),
        )

    # Status Choices
    OK = 'OK'
    DEAD = 'DE'
    UNCONSCIOUS = 'UC'
    status_choices = (
        (OK, 'OK'),
        (DEAD, 'Dead'),
        (UNCONSCIOUS, 'Unconscious')
        )

    # Gender Choices
    MALE = 'M'
    FEMALE = 'F'
    UNKNOWN = 'U'
    gender_choices = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (UNKNOWN, 'Unknown')
        )

    # Race Choices
    HUMAN = 'HU'
    ELF = 'EL'
    DWARF = 'DW'
    HALFELF = 'HE'
    HALFLING = 'HL'
    GNOME = 'GN'
    race_choices = (
        (HUMAN, 'Human'),
        (ELF, 'Elf'),
        (DWARF, 'Dwarf'),
        (HALFELF, 'Half Elven'),
        (HALFLING, 'Halfling'),
        (GNOME, 'Gnome')
        )

    # Target Categories
    ENEMY = 'E'
    FRIEND = 'F'
    NONE = 'N'

    name = models.CharField(max_length=200)
    world = models.ForeignKey(World)
    charclass = models.CharField(max_length=5, choices=charclass_choices)
    race = models.CharField(max_length=2, choices=race_choices, default=HUMAN)
    gender = models.CharField(max_length=1, choices=gender_choices, default=UNKNOWN)
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
    status = models.CharField(max_length=2, choices=status_choices, default=OK)

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

    ##########################################################################
    def __str__(self):
        return "{} {} ({}/{}) (Level {} {})".format(self.name, self.get_status_display(), self.hp, self.max_hp, self.level, self.get_charclass_display())

    ##########################################################################
    def generate_stats(self):
        if self.stat_str < 0:
        self.stat_str = self.roll_stat()
        if self.stat_str == 18:
            self.bonus_str = random.randint(1, 100)
        if self.stat_dex < 0:
        self.stat_dex = self.roll_stat()
        if self.stat_int < 0:
        self.stat_int = self.roll_stat()
        if self.stat_con < 0:
        self.stat_con = self.roll_stat()
        if self.stat_wis < 0:
        self.stat_wis = self.roll_stat()
        if self.stat_cha < 0:
        self.stat_cha = self.roll_stat()

    ##########################################################################
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
        self.ac = self.calc_ac()
        super(Character, self).save(**kwargs)

    ##########################################################################
    def calc_movement(self):
        # TODO: Encumbrance
        return tables.race[self.race]['movement']

    ##########################################################################
    def calc_hp(self):
        """ Calculate the HP for a level - try and make it not suck too much """
        if self.charclass == self.FIGHTER:
            index = 1
        else:
            index = 0
        return max(roll(self.hitdie()), roll(self.hitdie())) + tables.con_hp_adjustment[self.stat_con][index]

    ##########################################################################
    def calc_encumb(self):
        enc = sum(x.weight for x in self.gear.all())
        return enc

    ##########################################################################
    def roll_stat(self):
        """ Roll 4d6 and return the sum of the top 3
        Method VI in the PHG
        """
        return sum(sorted([roll('d6'), roll('d6'), roll('d6'), roll('d6')])[1:])

    ##########################################################################
    def learnSpell(self, spell):
        s = SpellState(character=self, spell=spell, memorized=True)
        s.save()
        self.save()

    ##########################################################################
    def castSpell(self, spell):
        ss = SpellState.objects.filter(memorized=True, spell=spell)
        if not ss:
            return False
        spell.cast(caster=self)
        ss[0].memorized = False
        ss[0].save()

    ##########################################################################
    def known_spells(self, level):
        s = Spell.objects.filter(spellstate__memorized=True, level=level)
        return s

    ##########################################################################
    def equip(self, obj, ready=False):
        e = EquipState(character=self, equipment=obj, ready=ready)
        e.save()
        self.save()

    ##########################################################################
    def equipped_weapon(self):
        """ Return the equiped weapon - currently only one weapon can be readied """
        e = Equipment.objects.filter(equipstate__ready=True, character=self, category=Equipment.WEAPON)
        if not e:
            return None
        return e[0]

    ##########################################################################
    def equipped_armour(self):
        """ Return the equiped armour """
        e = Equipment.objects.filter(equipstate__ready=True, character=self, category=Equipment.ARMOUR)
        return e

    ##########################################################################
    def hit(self, victim):
        hitroll = roll('d20')
        to_hit = self.thaco - victim.ac
        self.equipped_weapon()
        if hitroll > to_hit:
            return True
        else:
            return False

    ##########################################################################
    def attack(self, victim):
        weap = self.equipped_weapon()
        if self.hit(victim):
            if not weap:
                dmg = 1
            else:
                dmg = weap.weapon_dmg()
            victim.hurt(dmg)
            return dmg
        else:
            return 0

    ##########################################################################
    def heal(self, dmg):
        """ Heal self """
        if self.status == self.DEAD:
            return False
        self.hp += dmg
        if self.hp > self.max_hp:
            self.hp = self.max_hp
        if self.status == self.UNCONSCIOUS and self.hp > 0:
            self.status = self.OK
        self.save()
        return True

    ##########################################################################
    def hurt(self, dmg):
        """ Be hurt. Return True if still ok """
        self.hp -= dmg
        if self.hp <= 0:
            self.status = self.UNCONSCIOUS
            if self.hp < -10:
                self.status = self.DEAD
            self.save()
            return False
        self.save()
        return True

    ##########################################################################
    def calc_ac(self):
        armour = self.equipped_armour()
        base = 10
        mod = 0
        dex = 0
        if armour:
            base = min([_.ac_base for _ in armour])
            mod = sum([_.ac_modifier for _ in armour])
        ac = base - mod - dex
        return ac

    ##########################################################################
    def calc_thaco(self):
        if self.charclass == self.THIEF:
            return 20 - int((self.level - 1) / 2)
        elif self.charclass == self.FIGHTER:
            return 21 - self.level
        elif self.charclass == self.MAGE:
            return 20 - int((self.level - 1) / 3)
        elif self.charclass == self.CLERIC:
            return 20 - int((self.level - 1) * 2 / 3)

    ##########################################################################
    def select_target(self, categ=NONE):
        pass

    ##########################################################################
    def hitdie(self):
        hd_map = {
                self.THIEF: 'd6',
                self.FIGHTER: 'd10',
                self.MAGE: 'd4',
                self.CLERIC: 'd8',
                }
        return hd_map[self.charclass]

# EOF
