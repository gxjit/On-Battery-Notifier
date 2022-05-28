from threading import Event, Timer, main_thread

from psutil import sensors_battery  # type: ignore
from pystray import Icon as icon

from data import data
from state import (
    getDelayMultiplier,
    getDelayStatus,
    getInitInterval,
    getReminderInterval,
    setReminderInterval,
)


def reportBattery(icn: icon):
    _, _, power_plugged = sensors_battery()  # type: ignore
    # power_plugged = False  # Testing
    if not power_plugged:
        icn.notify(data.notifiction, data.appTitle)
        Event().wait(5)
        icn.remove_notification()
    else:
        setReminderInterval(getInitInterval())


def checkBattery(icn: icon):
    icn.visible = True

    t = None
    while True:

        if t is None or not t.is_alive():
            if getDelayStatus() and (t is not None):
                waitFor = getReminderInterval() * getDelayMultiplier()
                setReminderInterval(waitFor)
            else:
                waitFor = getInitInterval()
            # print(waitFor)
            t = Timer(waitFor, reportBattery, [icn])
            t.start()

        if not main_thread().is_alive():
            t.cancel()
            break

        Event().wait(2)
