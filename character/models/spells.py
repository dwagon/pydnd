from django.db import models
import importlib.util
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
        print("cwd={}".format(os.getcwd()))
        print("listdir={}".format(os.listdir('spells')))
        print("listdir={}".format(os.listdir('spells/{}'.format(self.get_charclass_display()))))
        print("listdir={}".format(os.listdir('spells/{}/level_{}'.format(self.get_charclass_display(), self.level))))
        fname = 'spells/{}/level_{}/{}.py'.format(self.get_charclass_display(), self.level, self.spellfile)
        spec = importlib.util.spec_from_file_location('spell', fname)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
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
