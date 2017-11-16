from BaseSpell import BaseSpell
from utils import roll


##############################################################################
class Spell_MagicMissile(BaseSpell):
    def __init__(self):
        BaseSpell.__init__(self)

    def cast(self, caster):
        num = int(caster.level / 2)
        dmg = roll('d4 + 1')
        for mis in range(0, num):
            target = caster.select_target(categ=caster.ENEMY)
            if target:
                target.hurt(dmg)

# EOF
