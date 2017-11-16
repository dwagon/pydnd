from django.db import models
import glob
import imp


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

    def __str__(self):
        return "{} (Level {})".format(self.name, self.level)

    def loadSpellFile(self):
        files = glob.glob('spells/{}/level_{}/*.py'.format(self.get_charclass_display(), self.level))
        for fname in files:
            if fname.startswith('_'):
                continue
            fname = fname.replace('.py', '')
            fp, pathname, desc = imp.find_module(fname)
            self.mod = imp.load_module(fname, fp, pathname, desc)
            print("mod={}".format(self.mod))

# EOF
