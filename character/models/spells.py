from django.db import models
import imp
import sys
import os


##############################################################################
class Spell(models.Model):
    # Character Class Choices
    FIGHTER = 'F'
    THIEF = 'T'
    MAGE = 'M'
    CLERIC = 'C'
    charclass_choices = (
        (MAGE, 'Mage'),
        (CLERIC, 'Cleric'),
        )

    name = models.CharField(max_length=200)
    level = models.IntegerField()
    charclass = models.CharField(max_length=5, choices=charclass_choices)
    spellfile = models.CharField(max_length=200)

    def __str__(self):
        return "{} (Level {})".format(self.name, self.level)

    def loadSpellKlass(self):
        fname = 'spells/{}/level_{}/{}.py'.format(self.get_charclass_display(), self.level, self.spellfile)
        fname = fname.replace('.py', '').replace('/', '.')
        print("cwd={}".format(os.getcwd()))
        fp, pathname, desc = imp.find_module(fname, ['.'])
        mod = imp.load_module(fname, fp, pathname, desc)
        classes = dir(mod)
        for c in classes:
            if c.startswith('Spell_'):
                klass = getattr(mod, c)
                break
        else:
            sys.stderr.write("Couldn't find Spell class in {}\n".format(fname))
            return None
        return klass

    def cast(self, caster):
        if not hasattr(self, 'klass'):
            self.klass = self.loadSpellKlass()
        k = self.klass()
        k.cast(caster)


# EOF
