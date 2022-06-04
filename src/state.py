reminderInterval = initInterval = 8 * 60
delayMultiplier = 2
delayEnabled = True


def toggleDealy():
    global delayEnabled
    delayEnabled = not delayEnabled


def getDelayStatus():
    return delayEnabled


def getDelayMultiplier():
    return delayMultiplier


def setDelayMultiplier(f: float):
    global delayMultiplier
    delayMultiplier = f


def getReminderInterval():
    return reminderInterval


def setReminderInterval(f: float):
    global reminderInterval
    reminderInterval = f


def getInitInterval():
    return initInterval


def setInitInterval(f: float):
    global initInterval
    initInterval = f
    setReminderInterval(f)
