from base64 import b64decode
from io import BytesIO
from functools import partial

from PIL import IcoImagePlugin  # for nuitka builds # noqa
from PIL import Image
from pystray import Icon as icon
from pystray import Menu as menu
from pystray import MenuItem as item

from lib.batteryThread import checkBattery
from lib.config import getConfigFile, loadConfig
from lib.data import data
from lib.dialogs import askSetTime, setDelay
from lib.state import getDelayStatus
from icon.icon import data as iconData

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

main = partial(trayIcon.run, checkBattery)

main()

# trayIcon.run(checkBattery)

# --windows-icon-from-ico=your-icon.png --show-modules
# --linux-onefile-icon=ICON_PATH nuitka -j --jobs=N os.cpu_count()
# --enable-plugin=tk-inter --windows-disable-console --mingw64/clang --msvc
# --icon=..\MLNMFLCN.ICO PyInstaller
