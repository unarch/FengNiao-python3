
import sys
import FengNiao
import Utils
import csv
import argparse

path = "."

extension = ["imageset", "jpg", "png", "gif", "pdf"]

excluded = ["Pods"]

fileExtension = ["h", "m", "mm", "swift", "xib", "storyboard", "plist"]

needSimilarCheck = False

def get_version():
    return '0.0.1'

def parse_args():
    parser = argparse.ArgumentParser(description="FengNiao is a simple command-line util\
        to deleting unused image resource files from your Xcode project.")
    parser.add_argument('-p', '--project', default='.', \
        help='Root path of your Xcode project. Default is current folder.' )
    parser.add_argument('-v', '--version', action='version', version = get_version(),\
        help='Print version.')
    parser.add_argument('-e', '--excluded', action='extend', type=str, nargs= '+', \
        help='Exclude paths from search. Default is [Pods].')
    parser.add_argument('-s', '--similar', action='store_true',\
        help='Need similar check. "image01" --similar-> "image%%02d" .')
    return parser.parse_args()

def main():
    fengniao = FengNiao.FengNiao(path, excluded, extension, fileExtension)
    fengniao.needSimilarCheck = needSimilarCheck
    print("path = ", fengniao.projectPath)
    print("need similar check = ", fengniao.needSimilarCheck)
    unusedFiles = []
    try:
        print("Searching unused file. This may take a while...")
        unusedFiles = fengniao.unusedFiles()
    except Exception as e:
        print("发送异常，异常原因为:",str(e))
        sys.exit(1)

    if len(unusedFiles) == 0:
        print("😎 Hu, you have no unused resources in path: ", fengniao.projectPath)
        return
    
    unusedFiles.sort(key = lambda x: x.size, reverse=True)

    unusedCSVFiles = [
            ["序号", "文件体积", "文件名称", "文件路径"]
        ]
    totalSize = 0
    for i, fileInfo in enumerate(unusedFiles):
        unusedItem = [i + 1 , fileInfo.readableSize(), fileInfo.fileName, fileInfo.path]
        unusedCSVFiles.append(unusedItem)
        totalSize += fileInfo.size

    totalHint = "{0} unused files are found. Total Size: {1} ".format(len(unusedFiles), Utils.fn_readableSize(totalSize))
    unusedCSVFiles.insert(0, [totalHint])
    print(totalHint)

    saveDirName = Utils.lastComponentWithoutExtension(fengniao.projectPath)

    unusedFileName = '{0}.csv'.format(saveDirName)

    with open(unusedFileName, "w", encoding='utf-8' ) as csvf:
        writer = csv.writer(csvf)
        writer.writerows(unusedCSVFiles)
    print("Bye!")


if __name__ == "__main__":
    args = parse_args()
    path = args.project
    needSimilarCheck = args.similar
    if args.excluded :
        excluded = args.excluded
    main()
