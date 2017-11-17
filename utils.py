import dice


def roll(dstr):
    """ Convert something like 1d6+3 into an appropriate random number """
    d = dice.roll(dstr)
    # Under some circumstances the roll returns an int otherwise an iterable object
    try:
        return sum(d)
    except TypeError:
        return d


# EOF
