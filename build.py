from argparse import ArgumentParser
from functools import partial
from os import chdir, environ
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

    runP(
        "curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -"  # noqa
    )

if system() == "Windows":
    if which("choco"):
        chocoDeps = f'{addNotWhich("upx")}'.strip()
        if pargs.pyinst and chocoDeps:
            runP(f"choco install {chocoDeps}")
        # if not which("python3"): # TODO
        #     runP("choco install python3")

    runP(
        "(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python -"  # noqa
    )

# runP(f"python -m pip install -U --user tomli")

rootPath = Path.cwd().resolve()
appEntry = rootPath.joinpath(data.entry)

chdir(rootPath)
runP("poetry install")

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
        f"poetry run python -m PyInstaller -y -n {data.appTitle} --distpath {buildPath} "
        f"--workpath {tempPath} --specpath {tempPath} --clean --onedir {appEntry}"
    )
elif pargs.nuitka:
    cmd = (
        f"poetry run python -m nuitka -n {data.appTitle} --standalone "
        f"--assume-yes-for-downloads --output-dir={buildPath} --remove-output {appEntry}"
    )
else:
    exit(1)


if pargs.onefile and pargs.pyinst:
    cmd = cmd.replace("--onedir", "--onefile")

if pargs.onefile and pargs.nuitka:
    cmd = cmd.replace("--standalone", "--onefile")

if zipPath.exists():
    zipPath.unlink()

# Build

runP(cmd)

if pargs.nuitka and not pargs.onefile:
    # nPath, *_ = [d for d in buildPath.iterdir() if str(d).endswith(".dist")]
    # nPath.rename
    buildPath.joinpath(f"{data.appTitle}.dist").rename(
        buildPath.joinpath(f"{data.appTitle}")
    )

if not distDir.exists():
    distDir.mkdir()

make_archive(str(zipPath.with_suffix("")), "zip", buildPath)

td.cleanup()

# build log
# 7zip compression?
# sudo in docker?
