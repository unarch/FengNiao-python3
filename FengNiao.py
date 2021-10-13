# -*- coding: utf-8 -*-

import os
from typing import Dict, List, Set
import Utils
import FileSearchRule


class FileInfo(object):
    size = 0
    fileName = ""
    path = ""

    def __init__(self, path: str) -> None:
        super().__init__()
        self.path = path
        self.size = Utils.fileSize(path)
        self.fileName = os.path.basename(path)
    
    def readableSize(self) -> str:
        return Utils.fn_readableSize(self.size)


class FengNiao(object):
    """
    #   需要额外的相似度检查
            // origin -> "image%02d"
            // used ->   "image01"
    """
    needSimilarCheck = False
    #   项目路径
    projectPath = ""
    #   不需要查找的路径
    excludedPaths = []
    #   需要查找的资源文件的扩展名
    resourceExtensions = []
    #   在哪些文件中搜索符号
    searchInFileExtensions = []
    #   需要排除的文件夹
    regularDirExtensions = ["imageset", "launchimage", "appiconset", "stickersiconset", "complicationset", "bundle"]

    def ___nonDirExtensions(self, ext) -> bool:
        return ext in self.resourceExtensions and ext not in self.regularDirExtensions

    def __init__(self, projectPath, excludedPaths, resourceExtensions, searchInFileExtensions) -> None:
        projectPath = os.path.abspath(projectPath)
        self.projectPath = projectPath
        self.excludedPaths = list(map(lambda x: os.path.join(projectPath, x), excludedPaths))
        self.resourceExtensions = resourceExtensions
        self.searchInFileExtensions = searchInFileExtensions

    def __listAllFiles(self, rootDir, extension) -> List[str]:
        """递归寻找目录下所有文件"""
        files = []
        dirList = os.listdir(rootDir)
        for subFile in dirList:
            path = os.path.join(rootDir, subFile)
            if path in self.excludedPaths:
                continue
            if Utils.fileExtension(path) in extension:
                files.append(path)
            if os.path.isdir(path):
                files.extend(self.__listAllFiles(path, extension))
        return files
    
    def allResourceFiles(self) -> Dict[str, Set[str]]:
        """ allResourceFiles
        获取所有的资源文件
        通过递归获取所有后缀符合的文件名，同时根据筛选条件来过滤掉其他的文件
        Args:
            extension    需要查找的资源扩展名
        Notes:
            对于在imageset等文件夹中的文件就直接过滤了
            因为在.m文件中是直接使用imageset文件夹名来做标识的
        Returns:
            返回值是一个字典(dict)格式 Key 是文件名 值是这个文件名的所有路径的集合
            example:
                {
                    "imageName1":set([
                        "/Users/root/files/imageName1.jpg"
                        "/Users/root/files/others/imageName1.imageset"
                    ]),
                }
        """
        extension = self.resourceExtensions
        result = self.__listAllFiles(self.projectPath, extension)

        fileDic = dict()
        dirPaths = list(map(lambda x: "." + x + "/", self.regularDirExtensions))
        for file in result:
            skip = list(map(lambda x : x in file, dirPaths))
            if True in skip:
                continue
            ext = Utils.fileExtension(file)
            if os.path.isdir(file) and self.___nonDirExtensions(ext):
                continue
            key = Utils.plainFileName(file, extension)
            if key in fileDic:
                fileDic[key].add(file)
            else:
                fileDic[key] = set([file])
        return fileDic
    
    def allUsedStringNames(self) -> Set[str]:
        return self.usedStringName(self.projectPath)
    
    def usedStringName(self, path) -> Set[str]:
        subPaths = os.listdir(path)
        result = []
        for subPath in subPaths:
            if subPath.startswith("."):
                continue
            subPath = os.path.join(path, subPath)
            if subPath in self.excludedPaths:
                continue
            if os.path.isdir(subPath):
                result.extend(self.usedStringName(subPath))
                continue
            fileExt = Utils.fileExtension(subPath)
            if fileExt not in self.searchInFileExtensions:
                continue
            fileType = FileSearchRule.FileTypeManage.fileType(fileExt)
            searchRules = FileSearchRule.FileTypeManage.searchRules(self.resourceExtensions, fileType)
            with open(subPath, "r", encoding= 'utf-8', errors= 'ignore') as f:
                content = f.read()
            for searchRule in searchRules:
                searchSet = searchRule.search(content)
                for name in searchSet:
                    ext = Utils.fileExtension(name)
                    if len(ext) == 0:
                        result.append(name)
                        continue
                    if ext in self.resourceExtensions:
                        result.append(Utils.lastComponentWithoutExtension(name))
                    else:
                        result.append(name)
        return set(result)

    def __similarCheck(self, origin, used) -> bool:
        """
            __similarCheck 判断是否有相似的字符串 
            // origin -> pattern "image%02d"
            // used -> name "image01"
            根据前缀后缀
        """
        if self.needSimilarCheck == False:
            return False
        for other in used:
            if Utils.similarPatternWithNumberIndex(other, origin):
                return True
        return False

    def filterUnused(self, all, used) -> List[str]:
        unusedPairs = {k: v for k, v in all.items() if k not in used and (self.__similarCheck(k, used) == False)}

        unusedList = [x for xlists in unusedPairs.values() for x in xlists]
        return unusedList

    def unusedFiles(self) -> List[FileInfo]:
        if len(self.resourceExtensions) == 0:
            raise Exception("需要查找的资源文件扩展名不能为空!!!!")
            return []
        if len(self.searchInFileExtensions) == 0:
            raise Exception("必须指定在哪些文件中查找!!! 比如「.m」文件")
            return []
        allResources = self.allResourceFiles()
        usedNames = self.allUsedStringNames()

        return list(map(lambda x: FileInfo(x), self.filterUnused(allResources, usedNames)))

