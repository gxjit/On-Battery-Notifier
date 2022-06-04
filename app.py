from base64 import b64decode
from io import BytesIO
from functools import partial

from PIL import IcoImagePlugin  # for nuitka builds # noqa
from PIL import Image
from pystray import Icon as icon
from pystray import Menu as menu
from pystray import MenuItem as item

from src.batteryThread import checkBattery
from src.config import getConfigFile, loadConfig
from src.data import data
from src.dialogs import askSetTime, setDelay
from src.state import getDelayStatus
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
