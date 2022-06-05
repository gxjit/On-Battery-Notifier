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


def take1(itr):
    return take(1, itr)[0]


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

if pargs.pyinst:
    cmd = (
        f"python -m poetry run python -m PyInstaller -y --strip "
        f'--distpath "{buildPath}" --workpath "{tempPath}" --specpath "{tempPath}"'
        f' -n "{data.appTitle}" --noconsole --clean --onedir {appEntry}'
    )
elif pargs.nuitka:
    cmd = (
        f"python -m poetry run python -m nuitka --standalone --assume-yes-for-downloads"
        f' --output-dir="{buildPath}" --remove-output "{appEntry}"'
        " --enable-plugin=tk-inter --windows-disable-console"
    )
else:
    exit(1)


if pargs.onefile and pargs.pyinst:
    cmd = cmd.replace("--onedir", "--onefile")

sfx = ".exe" if system() == "Windows" else ""

if pargs.onefile and pargs.nuitka:
    cmd = cmd.replace("--standalone", "--onefile")
    exePath = buildPath / f"{data.appTitle}{sfx}"
    cmd = cmd.replace(f'--output-dir="{buildPath}"', f'-o "{exePath}"')

if zipPath.exists():
    zipPath.unlink()

# Build

runP(cmd)

if pargs.nuitka and not pargs.onefile:
    nPath = take1(buildPath.glob("*.dist"))
    # nPath = [d for d in buildPath.iterdir() if str(d).endswith(".dist")][0]
    nPath = nPath.rename(buildPath / f"{data.appTitle}")

    exePath = take1(nPath.glob(f'{data.entry.replace(".py", "")}{sfx}'))
    exePath.rename(nPath / f"{data.appTitle}{sfx}")
    # [d for d in buildPath.iterdir() if str(d).startswith(".dist")][0]
    # rename exe?

if pargs.nuitka and pargs.onefile:
    exePath = take1(buildPath.glob(f'{data.entry.replace(".py", "")}{sfx}'))
    exePath.rename(buildPath / f"{data.appTitle}{sfx}")


if not distDir.exists():
    distDir.mkdir()

make_archive(str(zipPath.with_suffix("")), "zip", buildPath)

td.cleanup()


# --windows-icon-from-ico=your-icon.png --show-modules
# --linux-onefile-icon=ICON_PATH nuitka -j --jobs=N os.cpu_count()
# --enable-plugin=tk-inter --windows-disable-console --mingw64/clang --msvc
# --icon=..\MLNMFLCN.ICO PyInstaller

# build log
# 7zip compression?
# sudo in docker?
