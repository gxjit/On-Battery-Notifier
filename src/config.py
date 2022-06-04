from json import dump, load
from pathlib import Path

from .state import (
    getDelayMultiplier,
    getDelayStatus,
    getInitInterval,
    setDelayMultiplier,
    setInitInterval,
    toggleDealy,
)


def getConfigFile(configPath: Path) -> list:

    if not configPath.exists():
        if not configPath.parent.exists():
            configPath.parent.mkdir()
        configPath.touch()
        saveConfigFile(configPath)

    with open(configPath) as cfg:
        configFile = load(cfg)

    return configFile


def saveConfigFile(configPath: Path):
    state = [getInitInterval(), getDelayStatus(), getDelayMultiplier()]
    with open(configPath, "w") as cfg:
        dump(state, cfg)


def loadConfig(configFile: list):
    setInitInterval(configFile[0])
    if getDelayStatus() != configFile[1]:
        toggleDealy()
    setDelayMultiplier(configFile[2])
