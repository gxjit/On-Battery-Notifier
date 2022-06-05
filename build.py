from argparse import ArgumentParser
from functools import partial
from os import environ
from pathlib import Path
from platform import machine, system
from shutil import make_archive, which
from subprocess import run
from tempfile import TemporaryDirectory
from itertools import islice

from src.data import data


def parseArgs():
    parser = ArgumentParser()
    buildSelect = parser.add_mutually_exclusive_group(required=True)
    buildSelect.add_argument("-pi", "--pyinst", action="store_true")
    buildSelect.add_argument("-n", "--nuitka", action="store_true")
    parser.add_argument("-o", "--onefile", action="store_true")
    parser.add_argument("-d", "--deps", action="store_true")

    return parser.parse_args()


pargs = parseArgs()

runP = partial(run, shell=True, check=True)


def addNotWhich(dep, altCheck=None):
    if altCheck:
        return dep if not which(altCheck) else ""
    else:
        return dep if not which(dep) else ""


def take(n, itr):
    return list(islice(itr, n))


def head(itr):
    return list(islice(itr, 1))[0]


# Install deps

if system() == "Linux":
    if which("apt-get"):
        aptDeps = (
            f'{addNotWhich("python3")} {addNotWhich("python-is-python3", "python")}'
        )
        if pargs.pyinst:
            aptDeps = f'{aptDeps} {addNotWhich("upx")}'
        aptDeps = aptDeps.strip()
        if aptDeps:
            runP(f"sudo apt-get install -y {aptDeps}")


if system() == "Windows":
    if which("choco"):
        chocoDeps = f'{addNotWhich("python3", "python")}'
        if pargs.pyinst:
            chocoDeps = f'{chocoDeps} {addNotWhich("upx")}'
        chocoDeps = chocoDeps.strip()
        if chocoDeps:
            runP(f"choco install {chocoDeps}")


# runP(f"python -m pip install -U --user tomli")

runP("python -m pip install --user poetry")
# or pipx install poetry

runP("python -m poetry install")

if pargs.deps:
    exit()

# Build Setup

rootPath = Path.cwd().resolve()
appEntry = rootPath.joinpath(data.entry)
td = TemporaryDirectory(ignore_cleanup_errors=True)
tempRoot = Path(td.name)
buildPath = tempRoot.joinpath("build")
tempPath = tempRoot.joinpath("tmp")
distDir = (
    Path(environ.get("dist_dir"))  # type: ignore
    if environ.get("dist_dir")
    else rootPath.joinpath("dist")
)

baseFileName = data.appTitle.replace(" ", "-")
platformStr = f"{system()}_{machine()}".lower()

if pargs.nuitka:
    platformStr = f"n_{platformStr}"

if pargs.onefile:
    platformStr = f"o_{platformStr}"

zipPath = distDir.joinpath(f"{baseFileName}_{platformStr}").with_suffix(".zip")

icnPath = rootPath / data.icoFile

if pargs.pyinst:
    cmd = (
        f"python -m poetry run python -m PyInstaller -y --strip "
        f'--distpath "{buildPath}" --workpath "{tempPath}" --specpath "{tempPath}"'
        f' -n "{data.appTitle}" --noconsole --clean --onedir {appEntry}'
        f' --icon="{icnPath}"'
    )
elif pargs.nuitka:
    cmd = (
        f"python -m poetry run python -m nuitka --standalone --assume-yes-for-downloads"
        f' --output-dir="{buildPath}" --remove-output "{appEntry}"'
        " --enable-plugin=tk-inter --windows-disable-console "
    )
else:
    exit(1)

if system() == "Windows" and pargs.nuitka:
    cmd = f'{cmd} --windows-icon-from-ico="{icnPath}"'

if system() == "Linux" and pargs.nuitka:
    cmd = f'{cmd} --linux-onefile-icon="{icnPath.with_suffix(".png")}"'


if pargs.onefile and pargs.pyinst:
    cmd = cmd.replace("--onedir", "--onefile")

if pargs.onefile and pargs.nuitka:
    cmd = cmd.replace("--standalone", "--onefile")
    # exePath = buildPath / f"{data.appTitle}{sfx}"
    # cmd = cmd.replace(f'--output-dir="{buildPath}"', f'-o "{exePath}"')

if zipPath.exists():
    zipPath.unlink()

# Build

runP(cmd)

if len(take(1, buildPath.iterdir())) < 1:
    exit(1)


sfx = ".exe" if system() == "Windows" else ""

if pargs.nuitka and not pargs.onefile:
    nPath = head(buildPath.glob("*.dist"))
    nPath = nPath.rename(buildPath / f"{data.appTitle}")

    exePath = head(nPath.glob(f'{data.entry.replace(".py", "")}{sfx}'))
    exePath.rename(nPath / f"{data.appTitle}{sfx}")

if pargs.nuitka and pargs.onefile:
    try:
        exePath = head(buildPath.glob(f'{data.entry.replace(".py", "")}{sfx}'))
    except IndexError:
        exePath = head(buildPath.glob(f'{data.entry.replace(".py", "")}.bin'))
    exePath.rename(buildPath / f"{data.appTitle}{sfx}")


if not distDir.exists():
    distDir.mkdir()

make_archive(str(zipPath.with_suffix("")), "zip", buildPath)

td.cleanup()


# build log
# 7zip compression?
# sudo in docker?
