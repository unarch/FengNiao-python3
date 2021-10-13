## FengNiao 检查项目中无用资源脚本
翻译自 https://github.com/onevcat/FengNiao
### 使用：
    ```
        python3 main.py -p /Users/Users/Desktop/project

        如果有疑似无用资源会被放入project路径目录名的csv文件中 eg:project.csv
    ```
### 支持一些参数
    ```
        python3 main.py -h
        -p, --project : 你当前项目的根路径, 默认: 当前脚本所在目录
        -e, --excluded: 项目中需要不需要筛查的目录 默认: ["Pods"]
        -s, --similar : 是否开启相似度排除 通过前缀后缀排除可能引用了的资源文件 默认: 关闭
                        例: "image01" 会被"image%02d" 给筛掉
        -v, --version : 当前脚本版本号
        -h, --help    : 输出帮助信息
        
    ```
### 基本逻辑
    ```
        通过筛选出所有资源文件的集合 - ALL
        以及通过正则表达式查找对应文件中的已使用资源集合 - USED 
        来做差集        - ALL - ALL ∩ USED

        资源文件类型 = "imageset", "jpg", "png", "gif", "pdf"
        查找文件源类型 = "h", "m", "mm", "swift", "xib", "storyboard", "plist"
    ```
