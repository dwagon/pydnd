from BaseSpell import BaseSpell


##############################################################################
class Spell_CLW(BaseSpell):
    def __init__(self):
        BaseSpell.__init__(self)

    def cast(self, caster):
        print("Cast by {}".format(caster))

# EOF
