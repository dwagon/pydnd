import dice


def roll(dstr):
    """ Convert something like 1d6+3 into an appropriate random number """
    return sum(dice.roll(dstr))

# EOF
