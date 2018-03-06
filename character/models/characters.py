from . import Spell
from . import tables
from constants import alignment_choices
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from equipment.models import Equipment
from utils import roll
import status


##############################################################################
class EquipState(models.Model):
    character = models.ForeignKey('Character', on_delete=models.CASCADE)
    ready = models.BooleanField(default=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

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

    world = models.ForeignKey('world.World', on_delete=models.CASCADE)

    name = models.CharField(max_length=200)
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
    status = models.CharField(max_length=2, choices=status.status_choices, default=status.UNDEF)

    x = models.IntegerField(default=-1)
    y = models.IntegerField(default=-1)

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

    gear = models.ManyToManyField('equipment.Equipment', blank=True, through=EquipState)
    spells = models.ManyToManyField('Spell', blank=True, through=SpellState)
    moves = models.IntegerField(default=-1)
    initiative = models.IntegerField(default=-1)
    attacks = models.IntegerField(default=-1)

    animate = True

    ##########################################################################
    def __lt__(self, a):
        return self.name < a.name

    ##########################################################################
    def __str__(self):
        return "{} {} ({}/{}) (Level {} {})".format(self.name, self.get_status_display(), self.hp, self.max_hp, self.level, self.get_charclass_display())

    ##########################################################################
    def generate_stats(self):
        """ Generate any missing stats while ensuring class minimums """
        if self.stat_str < 0:
            self.stat_str = self.roll_stat()
            if self.stat_str == 18:
                self.bonus_str = random.randint(1, 100)
            if self.charclass == self.FIGHTER:
                self.stat_str = max(9, self.stat_str)
        if self.stat_dex < 0:
            self.stat_dex = self.roll_stat()
            if self.charclass == self.THIEF:
                self.stat_dex = max(9, self.stat_dex)
        if self.stat_int < 0:
            self.stat_int = self.roll_stat()
            if self.charclass == self.MAGE:
                self.stat_int = max(9, self.stat_int)
        if self.stat_con < 0:
            self.stat_con = self.roll_stat()
        if self.stat_wis < 0:
            self.stat_wis = self.roll_stat()
            if self.charclass == self.CLERIC:
                self.stat_wis = max(9, self.stat_wis)
        if self.stat_cha < 0:
            self.stat_cha = self.roll_stat()

    ##########################################################################
    def save(self, *args, **kwargs):
        if self.id is None or self.status == status.UNDEF:
            self.generate_stats()
            if self.max_hp == 0:
                self.max_hp = self.calc_hp()
                self.hp = self.max_hp
            self.status = status.OK
            # Need to save first to make M2M work on new objects
            super(Character, self).save(*args, **kwargs)
            # Stop restframework double insert
            kwargs['force_insert'] = False
        self.encumbrance = self.calc_encumb()
        self.movement = self.calc_movement()
        self.thaco = self.calc_thaco()
        self.ac = self.calc_ac()
        super(Character, self).save(*args, **kwargs)

    ##########################################################################
    def calc_movement(self):
        # TODO: Encumbrance
        return tables.race[self.race]['movement']

    ##########################################################################
    def get_reach(self):
        weap = self.equipped_weapon()
        if not weap:
            return 0
        return weap.reach

    ##########################################################################
    def calc_hp(self):
        """ Calculate the HP for a level - try and make it not suck too much """
        hp = max(roll(self.hitdie()), roll(self.hitdie()))
        hp += self.stat_bonus('hp_adj')
        hp = max(1, hp)
        return hp

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
    def learn_spell(self, spell):
        s = SpellState(character=self, spell=spell, memorized=True)
        s.save()
        self.save()

    ##########################################################################
    def cast_spell(self, spell):
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
        return e

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
        # TODO
        e = Equipment.objects.filter(equipstate__ready=True, character=self)
        return e

    ##########################################################################
    def hit(self, victim, mod=0):
        hitroll = roll('d20')
        hitroll += mod
        to_hit = self.thaco - victim.ac
        self.equipped_weapon()
        if hitroll > to_hit:
            return True
        else:
            return False

    ##########################################################################
    def attack(self, victim):
        weap = self.equipped_weapon()
        if not weap or weap.reach == 0:
            return self.melee_attack(weap, victim)
        else:
            return self.ranged_attack(weap, victim)

    ##########################################################################
    def ranged_attack(self, weap, victim):
        mod = self.stat_bonus('missattack')
        if self.hit(victim, mod):
            dmg = weap.weapon_dmg()
            dmg += self.stat_bonus('missattack')
            victim.hurt(dmg)
            return dmg
        else:
            return 0

    ##########################################################################
    def melee_attack(self, weap, victim):
        mod = self.stat_bonus('hitprob')
        if self.hit(victim, mod):
            if not weap:
                dmg = 1
            else:
                dmg = weap.weapon_dmg()
            dmg += self.stat_bonus('dmgadj')
            victim.hurt(dmg)
            return dmg
        else:
            return 0

    ##########################################################################
    def stat_bonus(self, bonus):
        if bonus in ('dmgadj', 'hitprob', 'weight'):
            if self.bonus_str >= 0:
                if self.bonus_str <= 50:
                    mod = tables.bonus_str_mods[50][bonus]
                elif self.bonus_str <= 75:
                    mod = tables.bonus_str_mods[75][bonus]
                elif self.bonus_str <= 90:
                    mod = tables.bonus_str_mods[90][bonus]
                elif self.bonus_str <= 99:
                    mod = tables.bonus_str_mods[99][bonus]
                else:
                    mod = tables.bonus_str_mods[100][bonus]
            else:
                mod = tables.str_mods[self.stat_str][bonus]
        if bonus in ('hp_adj',):
            if self.charclass == self.FIGHTER:
                index = 1
            else:
                index = 0
            mod = tables.con_mods[self.stat_con][bonus][index]
        if bonus in ('missattack', 'defadj'):
            mod = tables.dex_mods[self.stat_dex][bonus]
        return mod

    ##########################################################################
    def heal(self, dmg):
        """ Heal self """
        if self.status == status.DEAD:
            return False
        self.hp += dmg
        if self.hp > self.max_hp:
            self.hp = self.max_hp
        if self.status == status.UNCONSCIOUS and self.hp > 0:
            self.status = status.OK
        self.save()
        return True

    ##########################################################################
    def hurt(self, dmg):
        """ Be hurt. Return True if still ok """
        self.hp -= dmg
        if self.hp <= 0:
            self.status = status.UNCONSCIOUS
            if self.hp < -10:
                self.status = status.DEAD
            self.save()
            return False
        self.save()
        return True

    ##########################################################################
    def calc_ac(self):
        pass
        # TODO

    ##########################################################################
    def earnXp(self, xp):
        self.xp += xp

    ##########################################################################
    def select_target(self, categ=NONE):
        pass

    ##########################################################################
    def move(self, dirn):
        # self.world.move(self, dirn)
        pass

    ##########################################################################
    def start_turn(self):
        self.generate_initiative()
        self.attacks = 1
        self.moves = self.movement
        self.save()

    ##########################################################################
    def generate_initiative(self):
        init = roll('d10') + self.stat_bonus('defadj')
        self.initiative = init
        self.save()
        return init

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
