

from typing import List
import Utils
import re
import enum
import os
import abc


class FileSearchRule(metaclass = abc.ABCMeta):
    @abc.abstractmethod
    def search(self, content):
        return set()

class RegPatternSearchRule(FileSearchRule):
    extensions = []
    patterns = []

    def search(self, content) -> set:
        result = set()
        for pattern in self.patterns:
            regex = re.compile(pattern,re.I)
            matchs = regex.findall(content)
            plains = list(map(lambda x : Utils.plainFileName(x, self.extensions), matchs))
            result.update(plains)
        return result
        pass
    # _instance_lock = threading.Lock()
    # def __new__(cls, *args, **kwargs):
    #     if not hasattr(cls, '_instance_dict'):
    #         RegPatternSearchRule._instance_dict = {}

    #     if str(cls) not in RegPatternSearchRule._instance_dict.keys():
    #         with RegPatternSearchRule._instance_lock:
    #             _instance = super.__new__(cls, *args, **kwargs)
    #             RegPatternSearchRule._instance_dict[str(cls)] = _instance

    #     return RegPatternSearchRule._instance_dict[str(cls)]


class PlainImageSearchRule(RegPatternSearchRule):
    def __init__(self, extensions) -> None:
        super().__init__()
        self.extensions = extensions
        if len(self.extensions) == 0:
            self.patterns = []
        else :
            joinedExt = "|".join(extensions)
            str = "\"(.+?)\\.(" + joinedExt + ")\""
            self.patterns = [str]

class ObjCImageSearchRule(RegPatternSearchRule):
    def __init__(self, extensions) -> None:
        super().__init__()
        self.extensions = extensions
        self.patterns = ["@\"(.*?)\"", "\"(.*?)\""]

class SwiftImageSearchRule(RegPatternSearchRule):
    def __init__(self, extensions) -> None:
        super().__init__()
        self.extensions = extensions
        self.patterns = ["\"(.*?)\""]

class XibImageSearchRule(RegPatternSearchRule):
    def __init__(self, extensions) -> None:
        super().__init__()
        self.extensions = []
        self.patterns = ["image name=\"(.*?)\"", "image=\"(.*?)\"", "value=\"(.*?)\""]

class PlistImageSearchRule(RegPatternSearchRule):
    def __init__(self, extensions) -> None:
        super().__init__()
        self.extensions = extensions
        self.patterns = ["<string>(.*?)</string>"]

class PbxprojImageSearchRule(RegPatternSearchRule):
    def __init__(self, extensions) -> None:
        super().__init__()
        self.extensions = extensions
        self.patterns = ["ASSETCATALOG_COMPILER_APPICON_NAME = \"?(.*?)\"?;", "ASSETCATALOG_COMPILER_COMPLICATION_NAME = \"?(.*?)\"?;"]


class FileType(enum.Enum):
    swift = 1
    objc = 2
    xib = 3
    plist = 4
    pbxproj = 5
    unknown = 0


class FileTypeManage(object):
    def fileType(ext) -> FileType:
        if ext in ["swift"]:
            return FileType.swift
        if ext in ["h", "m", "mm"]:
            return FileType.objc
        if ext in ["xib", "storyboard"]:
            return FileType.xib
        if ext in ["plist"]:
            return FileType.plist
        if ext in ["pbxproj"]:
            return FileType.pbxproj
        return FileType.unknown
    
    def searchRules(extensions :List[str], fileType: FileType) -> List[FileSearchRule]:
        if FileType.swift is fileType:
            return[SwiftImageSearchRule(extensions)]
        if FileType.objc is fileType:
            return [ObjCImageSearchRule(extensions)]
        if FileType.xib is fileType:
            return [XibImageSearchRule(extensions)]
        if FileType.plist is fileType:
            return [PlistImageSearchRule(extensions)]
        if FileType.pbxproj is fileType:
            return [PbxprojImageSearchRule(extensions)]
        return [PlainImageSearchRule(extensions)]

