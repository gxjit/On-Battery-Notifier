from base64 import b64decode
from dataclasses import dataclass
from functools import partial
from io import BytesIO
from threading import Event, Timer, main_thread

from easygui import enterbox, msgbox
from PIL import IcoImagePlugin  # for nuitka builds # noqa
from PIL import Image
from psutil import sensors_battery  # type: ignore
from pystray import Icon as icon
from pystray import Menu as menu
from pystray import MenuItem as item

from icon.icon import data
from state import (
    getDelayMultiplier,
    getDelayStatus,
    getInitInterval,
    getReminderInterval,
    setDelayMultiplier,
    setInitInterval,
    setReminderInterval,
    toggleDealy,
)

appTitle = "On Battery Notifier"

iconImage = Image.open(BytesIO(b64decode(data)))


@dataclass
class Messages:
    exit = "Exit"
    setInterval = "Set reminder interval"
    enableDelaying = "Enable Delaying subsequent notifications"
    notifiction = "System is not plugged to an AC Source."
    remindAfter = "Remind me after x minutes?"
    delayMultiplier = "Delay subsequent notifications by previous inteval * x."
    invalid = "Invalid Input."


messages = Messages()

round2 = partial(round, ndigits=2)


def askSetTime():
    try:
        t = enterbox(
            messages.remindAfter, appTitle, str(round2(getInitInterval() / 60))
        )
        setInitInterval(float(t) * 60)
        if getDelayStatus():
            i = enterbox(messages.delayMultiplier, appTitle, str(getDelayMultiplier()))
            setDelayMultiplier(float(i))
    except (ValueError, TypeError):
        msgbox(messages.invalid, appTitle)


def reportBattery(icn: icon):
    # _, _, power_plugged = sensors_battery()  # type: ignore
    power_plugged = False  # Testing
    if not power_plugged:
        icn.notify(messages.notifiction, appTitle)
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
            print(waitFor)  # unplugged check
            t = Timer(waitFor, reportBattery, [icn])
            t.start()

        if not main_thread().is_alive():
            t.cancel()
            break

        Event().wait(2)


trayIcon = icon(
    appTitle,
    iconImage,
    appTitle,
    menu=menu(
        item(messages.exit, lambda icn: icn.stop()),
        item(messages.setInterval, askSetTime),
        item(
            messages.enableDelaying,
            lambda i: toggleDealy(),
            checked=lambda i: getDelayStatus(),
        ),
    ),
)

trayIcon.SETUP_THREAD_TIMEOUT = 3

trayIcon.run(checkBattery)

# --windows-icon-from-ico=your-icon.png
# --linux-onefile-icon=ICON_PATH nuitka -j --jobs=N os.cpu_count()
# --enable-plugin=tk-inter --windows-disable-console --mingw64/clang --msvc
# --icon=..\MLNMFLCN.ICO PyInstaller
