from django.test import TestCase
from monster.models import Monster, MonsterAttack
from equipment.models import Armour
from encounter.models import Encounter
from character.models import Wizard
from world.models import World


class test_Monster(TestCase):
    def setUp(self):
        self.w = World()
        self.w.save()
        self.orc = Monster(name="Orc", align="CE", size="M", ac=13, hitdie="2d8 + 6", speed=30, stat_str=16, stat_dex=12, stat_con=16, stat_int=7, stat_wis=11, stat_cha=10, challenge="1/2")
        self.orc.save()
        self.greataxe = MonsterAttack(monster=self.orc, name="greataxe", desc="Sharp", to_hit=5, reach=5, damage="1d12+3", damage_cat="S", normal_range=0, long_range=0)
        self.greataxe.save()
        self.enc = Encounter(world=self.w)
        self.enc.save()

    def tearDown(self):
        self.orc.delete()
        self.enc.delete()
        self.w.delete()

    def test_speed(self):
        self.assertEqual(self.orc.speed, 30)

    def test_hit(self):
        arm = Armour(name='useless', base_ac=3, armour_categ='L')
        arm.save()
        wiz = Wizard(world=self.w, name='victim', max_hp=10, hp=10)
        wiz.save()
        wiz.equip(arm, ready=True)
        self.enc.add_monster_type('Orc')
        this_orc = self.enc.all_monsters()[0]
        dmg = this_orc.attack(wiz)
        self.assertEqual(len(dmg), 1)
        self.assertEqual(dmg[0][1], 'S')
        self.assertGreaterEqual(dmg[0][0], 4)
        self.assertLessEqual(dmg[0][0], 15)
        wiz.delete()
        arm.delete()

    def test_miss(self):
        e = Armour(name='impervious', base_ac=30, armour_categ='H')
        e.save()
        c = Wizard(world=self.w, name='victim')
        c.save()
        c.equip(e, ready=True)
        c.ac = -30    # Guarantee miss
        c.save()
        self.enc.add_monster_type('Orc')
        this_orc = self.enc.all_monsters()[0]
        hit = this_orc.attack(c)
        self.assertFalse(hit)

# EOF
