from BaseSpell import BaseSpell
from utils import roll


##############################################################################
class Spell_CLW(BaseSpell):
    def __init__(self):
        BaseSpell.__init__(self)

    def cast(self, caster):
        print("Cast by {}".format(caster))
        # TODO select someone else
        caster.heal(roll('d6'))

# EOF
