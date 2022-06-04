from argparse import ArgumentParser
from functools import partial
from os import environ
from pathlib import Path
from platform import machine, system
from shutil import make_archive, which
from subprocess import run
from tempfile import TemporaryDirectory

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


def addNotWhich(dep: str) -> str:
    return dep if not which(dep) else ""


# Install deps

if system() == "Linux":
    if which("apt-get"):
        aptDeps = f'{addNotWhich("python3")} {addNotWhich("python-is-python3")}'
        if pargs.pyinst:
            aptDeps = f'{aptDeps} {addNotWhich("upx")}'
        aptDeps = aptDeps.strip()
        if aptDeps:
            runP(f"sudo apt-get install -y {aptDeps}")


if system() == "Windows":
    if which("choco"):
        chocoDeps = f'{addNotWhich("upx")}'.strip()
        if pargs.pyinst and chocoDeps:
            runP(f"choco install {chocoDeps}")

        # if not which("python3"): # TODO
        #     runP("choco install python3")


# runP(f"python -m pip install -U --user tomli")

runP("python -m pip install --user poetry")
# or pipx install poetry

rootPath = Path.cwd().resolve()
appEntry = rootPath.joinpath(data.entry)

runP("python -m poetry install")

if pargs.deps:
    exit()

# Build Setup

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
        f"python -m poetry run python -m PyInstaller -y "
        f'-n "{data.appTitle}" --distpath "{buildPath}" '
        f'--workpath "{tempPath}" --specpath "{tempPath}" --clean --onedir {appEntry}'
    )
elif pargs.nuitka:
    cmd = (
        f"python -m poetry run python -m nuitka --standalone --assume-yes-for-downloads"
        f' --output-dir="{buildPath}" --remove-output "{appEntry}"'
        "--enable-plugin=tk-inter --windows-disable-console"
    )
else:
    exit(1)


if pargs.onefile and pargs.pyinst:
    cmd = cmd.replace("--onedir", "--onefile")

if pargs.onefile and pargs.nuitka:
    cmd = cmd.replace("--standalone", f'--onefile -o "{data.appTitle}"')

if zipPath.exists():
    zipPath.unlink()

# Build

runP(cmd)

if pargs.nuitka and not pargs.onefile:
    nPath = [d for d in buildPath.iterdir() if str(d).endswith(".dist")][0]
    nPath.rename(buildPath.joinpath(f"{data.appTitle}"))
    # buildPath.joinpath(f"{data.appTitle}.dist").rename(
    #     buildPath.joinpath(f"{data.appTitle}")
    # )
    # rename exe?

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
