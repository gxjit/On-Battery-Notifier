from functools import partial

from easygui import enterbox, msgbox

from data import data
from state import (
    getDelayMultiplier,
    getDelayStatus,
    getInitInterval,
    setDelayMultiplier,
    setInitInterval,
)

round2 = partial(round, ndigits=2)


def askSetTime():
    try:
        t = enterbox(
            data.remindAfter, data.appTitle, str(round2(getInitInterval() / 60))
        )
        setInitInterval(float(t) * 60)
        if getDelayStatus():
            i = enterbox(data.delayMultiplier, data.appTitle, str(getDelayMultiplier()))
            setDelayMultiplier(float(i))
    except (ValueError, TypeError):
        msgbox(data.invalid, data.appTitle)
