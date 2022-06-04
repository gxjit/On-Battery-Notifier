from dataclasses import dataclass
from pathlib import Path


@dataclass
class Data:
    appTitle = "On Battery Notifier"
    appVersion = "0.1.1"
    appDescription = (
        "Sends tray notifications when system is not plugged to an AC Source"
    )
    " i.e. running on a battery source."
    authors = ["Gurjit Singh <g.s@outlook.in>"]
    license = "MIT"
    entry = "app.py"
    icoFile = "icon/icon.ico"

    notifiction = "System is not plugged to an AC Source."
    setInterval = "Set reminder interval"
    enableDelaying = "Enable Delaying subsequent notifications"
    remindAfter = "Remind me after x minutes?"
    delayMultiplier = "Delay subsequent notifications by previous inteval * x."
    invalid = "Invalid Input."
    exit = "Exit"

    def getConfigFile(self):
        return Path.home() / ".config" / f"{self.appTitle}.json"


data = Data()
