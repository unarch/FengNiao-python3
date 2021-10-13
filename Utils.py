from functools import reduce
import os
from typing import List
import re

def plainFileName(path: str, extensions: List[str]) -> str:
    result = None
    for ext in extensions:
        if path.endswith(ext):
            result = lastComponentWithoutExtension(path)
            break
    if result == None:
        result = os.path.basename(path)
    if result.endswith("@2x") or result.endswith("@3x"):
        result = result[:-3]
    return result

def fileExtension(path: str) -> str: 
    ext = os.path.splitext(path)[1]
    if len(ext) and ext[0] == ".":
        ext = ext[1:]
    return ext

def lastComponentWithoutExtension(path: str) -> str:
    result = os.path.basename(path)
    result = os.path.splitext(result)[0]
    return result

fileSizeSuffix = ["B", "KB", "MB", "GB"]
def fn_readableSize(size: int) -> str:
    level = 0
    while size > 1000.0 and level < 3 :
        level = level + 1
        size = size / 1000.0
    if level == 0:
        return "{} {}".format(size, fileSizeSuffix[level])
    else:
        return "{:.2f} {}".format(size, fileSizeSuffix[level])

def fileSize(path: str) -> int:
    if os.path.isdir(path):
        subPaths = os.listdir(path)
        subPaths = list(map(lambda x: fileSize(os.path.join(path, x)), subPaths))
        return reduce(lambda x,y : x + y, subPaths)
    else:
        if os.path.basename(path).startswith("."):
            return 0
        return os.path.getsize(path)

regex = re.compile("(\\d+)",re.I)

def similarPatternWithNumberIndex(origin, other) -> bool:
    matchs = regex.findall(other)
    if len(matchs) == 0: return False
    lastMatch = matchs[-1]
    digitalLocation = other.rfind(lastMatch)
    prefix = None
    if digitalLocation != 0 :
        prefix = other[ : digitalLocation]

    digitalMaxRange = digitalLocation + len(lastMatch)
    suffix = None
    if digitalMaxRange < len(other):
        suffix = other[digitalMaxRange : ]

    if prefix != None and suffix == None:
        return origin.startswith(prefix)
    elif prefix == None and suffix != None:
        return origin.endswith(suffix)
    elif prefix != None and suffix != None:
        return origin.startswith(prefix) and origin.endswith(suffix)
    else:
        return False
