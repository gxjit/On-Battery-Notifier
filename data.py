from dataclasses import dataclass
from pathlib import Path


@dataclass
class Data:
    appTitle = "On Battery Notifier"
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
