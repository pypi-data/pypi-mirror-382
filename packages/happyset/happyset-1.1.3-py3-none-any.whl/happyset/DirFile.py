import shutil
from pathlib import Path

# Clear
def Clear_dir(path :str|Path) -> None:
    shutil.rmtree(path)
    if type(path) is str:
        path = Path(path)
    path.mkdir()
    
def Clear_file(path :str|Path) -> None:
    with open(path, "r+") as f:
        f.truncate(0)

# Copy
def Copy_dir(targetPath :str|Path, createPath :str|Path) -> None:
    shutil.copytree(targetPath, createPath, dirs_exist_ok=True)

# Move
def Move_file(srcpath :str|Path, dstpath :str|Path) -> None:
    shutil.move(srcpath, dstpath)
