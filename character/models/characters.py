from . import Spell
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from gm2m import GM2MField
from utils import roll
from pydnd.models import Creature, CreatureState
import status
import sys


##############################################################################
class EquipState(models.Model):
    character = models.ForeignKey('Character', on_delete=models.CASCADE)
    content_object = GenericForeignKey(ct_field='content_type', fk_field='object_id')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    ready = models.BooleanField(default=False)

    def __str__(self):
        return "{}'s {}".format(self.character.name, self.equipment.name)


##############################################################################
class SpellState(models.Model):
    character = models.ForeignKey('Character', on_delete=models.CASCADE)
    spell = models.ForeignKey(Spell, on_delete=models.CASCADE)
    prepared = models.BooleanField(default=False)
    default = models.BooleanField(default=False)

    def __str__(self):
        prepstr = ""
        if self.prepared:
            prepstr = "prepared "
        return "{}'s {}{}".format(self.character.name, prepstr, self.spell.name)


##############################################################################
def Fighter(**kwargs):
    return Character(charclass=Character.FIGHTER, **kwargs)


##############################################################################
def Rogue(**kwargs):
    return Character(charclass=Character.ROGUE, **kwargs)


##############################################################################
def Wizard(**kwargs):
    return Character(charclass=Character.WIZARD, **kwargs)


##############################################################################
def Cleric(**kwargs):
    return Character(charclass=Character.CLERIC, **kwargs)


##############################################################################
class Character(Creature, CreatureState):
    # Character Class Choices
    BARBARIAN = 'BB'
    BARD = 'BD'
    CLERIC = 'CL'
    DRUID = 'DR'
    FIGHTER = 'FG'
    MONK = 'MK'
    PALADIN = 'PL'
    RANGER = 'RA'
    ROGUE = 'RO'
    SORCEROR = 'SO'
    WARLOCK = 'WA'
    WIZARD = 'WZ'
    charclass_choices = (
        (BARBARIAN, 'Barbarian'),
        (BARD, 'Bard'),
        (CLERIC, 'Cleric'),
        (DRUID, 'Druid'),
        (FIGHTER, 'Fighter'),
        (MONK, 'Monk'),
        (PALADIN, 'Paladin'),
        (RANGER, 'Ranger'),
        (ROGUE, 'Rogue'),
        (SORCEROR, 'Sorceror'),
        (WARLOCK, 'Warlock'),
        (WIZARD, 'Wizard'),
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

    world = models.ForeignKey('world.World', on_delete=models.CASCADE, related_name='pcs')

    charclass = models.CharField(max_length=5, choices=charclass_choices)
    race = models.CharField(max_length=3, choices=race_choices, default=HUMAN)
    subrace = models.CharField(max_length=3, choices=race_choices, default=NONE)
    gender = models.CharField(max_length=1, choices=gender_choices, default=UNKNOWN)
    dmg = models.IntegerField(default=1)
    encumbrance = models.IntegerField(default=0)
    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    proficiency = models.IntegerField(default=-1)

    plat = models.IntegerField(default=0)
    gold = models.IntegerField(default=0)
    silver = models.IntegerField(default=0)
    copper = models.IntegerField(default=0)

    gear = GM2MField(through='EquipState')
    spells = models.ManyToManyField('Spell', blank=True, through=SpellState)

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
        self.speed = self.calc_speed()
        self.ac = self.calc_ac()
        super(Character, self).save(*args, **kwargs)

    ##########################################################################
    def calc_speed(self):
        # TODO: Race
        return 30

    ##########################################################################
    def get_reach(self):
        weaps = self.equipped_weapon()
        for weap in weaps:
            if weap.normal_range:
                return (weap.normal_range, weap.long_range)
        return 0, 0

    ##########################################################################
    def calc_hp(self):
        """ Calculate the HP for a level - try and make it not suck too much """
        if self.level == 1:
            hp = int(self.hitdie().replace('d', ''))
        else:
            hp = max(roll(self.hitdie()), roll(self.hitdie()))
        hp += self.stat_bonus(self.stat_con)
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
        s = SpellState(character=self, spell=spell, prepared=True)
        s.save()
        self.save()

    ##########################################################################
    def cast_spell(self, spell):
        ss = SpellState.objects.filter(prepared=True, spell=spell)
        if not ss:
            return False
        spell.cast(caster=self)
        ss[0].prepared = False
        ss[0].save()

    ##########################################################################
    def known_spells(self, level):
        s = Spell.objects.filter(spellstate__prepared=True, level=level)
        return s

    ##########################################################################
    def equip(self, obj, ready=False):
        e = EquipState(character=self, content_object=obj, ready=ready)
        e.save()
        self.save()
        return e

    ##########################################################################
    def equipped_weapon(self):
        """ Return the equipped weapon """
        from equipment.models.weapon import Weapon
        e = self.gear.filter(ready=True).filter(Model=Weapon)
        return e

    ##########################################################################
    def equipped_armour(self):
        """ Return the equipped armour """
        from equipment.models.armour import Armour
        e = self.gear.filter(ready=True).filter(Model=Armour)
        return e

    ##########################################################################
    def hit(self, victim, mod=0):
        hitroll = roll('d20')
        hitroll += mod
        if hitroll > victim.ac:
            return True
        else:
            return False

    ##########################################################################
    def attack(self, victim):
        weaps = self.equipped_weapon()
        damages = []
        for weap in weaps:
            if weap.normal_range == 0:
                damages.append(self.melee_attack(weap, victim))
            else:
                damages.append(self.ranged_attack(weap, victim))
        return damages

    ##########################################################################
    def ranged_attack(self, weap, victim):
        mod = self.stat_bonus(self.stat_dex)
        if self.hit(victim, mod):
            dmg = roll(weap.damage)
            dmg += self.stat_bonus(self.stat_dex)
            victim.hurt(dmg, weap.damage_cat)
            return dmg, weap.damage_cat
        else:
            return 0, None

    ##########################################################################
    def melee_attack(self, weap, victim):
        mod = self.stat_bonus(self.stat_str)
        mod += self.proficiency
        if self.hit(victim, mod):
            if not weap:
                dmg = 1
            else:
                dmg = roll(weap.damage)
            dmg += self.stat_bonus(self.stat_str)
            victim.hurt(dmg, weap.damage_cat)
            return dmg, weap.damage_cat
        else:
            return 0, None

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
    def hurt(self, dmgs):
        """ Be hurt. Return True if still ok """
        for dmg in dmgs:
            self.hp -= dmg[0]
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
        """ Calculate the characters AC """
        armours = self.equipped_armour()
        if not armours:
            ac = 10 + self.stat_bonus(self.stat_dex)
            return ac
        ac = 10
        for armour in armours:
            if armour.categ() != 'Shield':
                ac = armour.calc_ac(self.stat_bonus(self.stat_dex))
        for armour in armours:
            if armour.categ() == 'Shield':
                ac += armour.calc_ac(self.stat_bonus(self.stat_dex))
        return ac

    ##########################################################################
    def earnXp(self, xp):
        self.xp += xp

    ##########################################################################
    def select_target(self, categ=NONE):
        pass

    ##########################################################################
    def move(self, direct):
        assert direct in 'NSEW'
        if direct == 'N':
            newx = self.x - 1
            newy = self.y
        elif direct == 'S':
            newx = self.x + 1
            newy = self.y
        elif direct == 'E':
            newx = self.x
            newy = self.y + 1
        elif direct == 'W':
            newx = self.x
            newy = self.y - 1
        t = self.world[(newx, newy)]
        if t is None:
            enc = Encounter.objects.filter(world=self.world)[0]
            enc.change_loc(self.x, self.y, newx, newy)
            self.x = newx
            self.y = newy
            self.save()

    ##########################################################################
    def start_turn(self):
        self.moves = self.speed
        self.save()

    ##########################################################################
    def take_action(self):
        pass

    ##########################################################################
    def initiative(self):
        init = roll('d20') + self.stat_bonus(self.stat_dex)
        return init

    ##########################################################################
    def hitdie(self):
        hd_map = {
                self.ROGUE: 'd8',
                self.FIGHTER: 'd10',
                self.WIZARD: 'd6',
                self.CLERIC: 'd8',
                }
        return hd_map[self.charclass]

# EOF
