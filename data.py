from dataclasses import dataclass


@dataclass
class Data:
    appTitle = "On Battery Notifier"
    exit = "Exit"
    setInterval = "Set reminder interval"
    enableDelaying = "Enable Delaying subsequent notifications"
    notifiction = "System is not plugged to an AC Source."
    remindAfter = "Remind me after x minutes?"
    delayMultiplier = "Delay subsequent notifications by previous inteval * x."
    invalid = "Invalid Input."


data = Data()
