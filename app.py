from base64 import b64decode
from io import BytesIO

from PIL import IcoImagePlugin  # for nuitka builds # noqa
from PIL import Image
from pystray import Icon as icon
from pystray import Menu as menu
from pystray import MenuItem as item

from icon.icon import data as iconData
from state import (
    getDelayStatus,
)
from data import data
from dialogs import askSetTime, setDelay
from batteryThread import checkBattery
from config import getConfigFile, loadConfig

loadConfig(getConfigFile(data.getConfigFile()))

iconImage = Image.open(BytesIO(b64decode(iconData)))


trayIcon = icon(
    data.appTitle,
    iconImage,
    data.appTitle,
    menu=menu(
        item(data.exit, lambda icn: icn.stop()),
        item(data.setInterval, askSetTime),
        item(
            data.enableDelaying,
            lambda i: setDelay(),
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
