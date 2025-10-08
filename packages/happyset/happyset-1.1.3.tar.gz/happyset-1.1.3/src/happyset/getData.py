import csv
from pathlib import Path

# csv
def Get_csv2List(path :str|Path) -> list:
    with open(path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        data = [data for data in reader]
    return data

# text
def Get_text2list(path :str|Path, delimiter :str) -> list:
    with open(path, 'r') as f:
        return f.read().split(delimiter)

# directory
def Get_dirList(path :str|Path) -> list:
    if type(path) is str:
        path = Path(path)
    return sorted([Path(f) for f in path.iterdir() if (path/f).is_dir()])

# file
def Get_fileList(path :str|Path) -> list:
    if type(path) is str:
        path = Path(path)
    return sorted([f for f in path.iterdir() if (path/f).is_file() and (not str(f).startswith("."))])

def Get_filepathList(path :str|Path):
    if type(path) is str:
        path = Path(path)
    return sorted([Path((path/f).absolute()) for f in path.iterdir() if (path/f).is_file() and (not str(f).startswith("."))])

def Get_uniqueList(targetList):
    return sorted(filter(lambda a: a != '',list(set(targetList))))

def Get_keysFromValue(d, val):
    return [k for k, v in d.items() if v == val]
