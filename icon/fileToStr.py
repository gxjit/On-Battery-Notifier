from base64 import b64encode
from pathlib import Path

inFileName = "icon.ico"
inFile = Path.cwd().resolve().joinpath(f"./{inFileName}")
outFile = inFile.with_suffix(".py")

data = b64encode(inFile.read_bytes())
outFile.write_text(f"data = {data}")
